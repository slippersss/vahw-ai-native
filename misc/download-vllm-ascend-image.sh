#!/usr/bin/env bash
# Manual utility for exporting a vLLM Ascend registry image as a Docker tar.
#
# 中文快速上手：
# 1. 脚本在 root 容器内运行；如果没有 skopeo，会尝试使用系统包管理器自动安装。
# 2. 如需代理，请在运行前设置 HTTP_PROXY、HTTPS_PROXY 和 NO_PROXY。
# 3. 按 tag 下载：
#      ./download-vllm-ascend-image.sh v0.23.0 /共享目录/images
# 4. 按 digest 锁定不可变镜像内容：
#      ./download-vllm-ascend-image.sh sha256:<64位摘要> /共享目录/images
# 5. 同时保留 tag 并校验 digest：
#      ./download-vllm-ascend-image.sh v0.23.0@sha256:<64位摘要> /共享目录/images
# 6. 默认下载 linux/arm64，默认关闭源 TLS 校验；可通过 IMAGE_ARCH 和
#    SOURCE_TLS_VERIFY 覆盖。生成的 tar 可在宿主机执行 docker load -i <文件>。
set -Eeuo pipefail

usage() {
    cat <<'EOF'
Usage: download-vllm-ascend-image.sh <tag-or-digest> [output-directory]

Accepted references:
  v0.23.0
  sha256:<64 hexadecimal characters>
  v0.23.0@sha256:<64 hexadecimal characters>

Environment variables:
  IMAGE_REPOSITORY  Source image repository.
                    Default: quay.io/ascend/vllm-ascend
  IMAGE_ARCH        Target image architecture. Default: arm64
  SOURCE_TLS_VERIFY Verify the source registry TLS certificate. Default: false
                    Set to true when the container trusts the complete chain.
  FORCE             Set to 1 to replace an existing tar file.

The script inherits HTTP_PROXY, HTTPS_PROXY, and NO_PROXY from its environment.
EOF
}

if [[ $# -lt 1 || $# -gt 2 ]]; then
    usage >&2
    exit 2
fi

install_skopeo() {
    if command -v skopeo >/dev/null 2>&1; then
        return
    fi

    if [[ $(id -u) -ne 0 ]]; then
        echo "Error: skopeo is missing and automatic installation requires root." >&2
        exit 127
    fi

    echo "skopeo is not installed; installing it now..."

    if command -v apt-get >/dev/null 2>&1; then
        apt-get update
        DEBIAN_FRONTEND=noninteractive apt-get install -y skopeo
    elif command -v dnf >/dev/null 2>&1; then
        dnf install -y skopeo
    elif command -v yum >/dev/null 2>&1; then
        yum install -y skopeo
    elif command -v zypper >/dev/null 2>&1; then
        zypper --non-interactive install skopeo
    elif command -v apk >/dev/null 2>&1; then
        apk add --no-cache skopeo
    else
        echo "Error: no supported package manager found to install skopeo." >&2
        exit 127
    fi

    if ! command -v skopeo >/dev/null 2>&1; then
        echo "Error: skopeo installation completed without providing the command." >&2
        exit 127
    fi
}

reference=$1
output_dir=${2:-$PWD}
repository=${IMAGE_REPOSITORY:-quay.io/ascend/vllm-ascend}
arch=${IMAGE_ARCH:-arm64}
source_tls_verify=${SOURCE_TLS_VERIFY:-false}
force=${FORCE:-0}

if [[ $source_tls_verify != true && $source_tls_verify != false ]]; then
    echo "Error: SOURCE_TLS_VERIFY must be true or false." >&2
    exit 2
fi

validate_tag() {
    local value=$1
    [[ $value =~ ^[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}$ ]]
}

digest_pattern='sha256:[0-9a-fA-F]{64}'

if [[ $reference =~ ^(${digest_pattern})$ ]]; then
    digest=${BASH_REMATCH[1],,}
    digest_hex=${digest#sha256:}
    source_image="${repository}@${digest}"
    archive_image="${repository}:digest-${digest_hex:0:12}"
    output_stem="digest-${digest_hex}"
elif [[ $reference =~ ^([^@]+)@(${digest_pattern})$ ]]; then
    tag=${BASH_REMATCH[1]}
    digest=${BASH_REMATCH[2],,}
    if ! validate_tag "$tag"; then
        echo "Error: invalid image tag in reference: $reference" >&2
        exit 2
    fi
    source_image="${repository}:${tag}@${digest}"
    archive_image="${repository}:${tag}"
    output_stem="${tag}-${digest#sha256:}"
elif validate_tag "$reference"; then
    tag=$reference
    source_image="${repository}:${tag}"
    archive_image=$source_image
    output_stem=$tag
else
    echo "Error: invalid tag or digest reference: $reference" >&2
    exit 2
fi

output_dir=$(mkdir -p "$output_dir" && cd "$output_dir" && pwd)
output_file="${output_dir}/vllm-ascend-${output_stem}-${arch}.tar"
partial_file="${output_file}.partial"

if [[ -e $output_file && $force != 1 ]]; then
    echo "Error: output already exists: $output_file" >&2
    echo "Set FORCE=1 to replace it." >&2
    exit 1
fi

install_skopeo

rm -f "$partial_file"
trap 'rm -f "$partial_file"' EXIT

echo "Source: docker://${source_image}"
echo "Archive reference: ${archive_image}"
echo "Platform: linux/${arch}"
echo "Source TLS verification: $source_tls_verify"
echo "Output: $output_file"

skopeo copy \
    --override-os linux \
    --override-arch "$arch" \
    "--src-tls-verify=${source_tls_verify}" \
    --retry-times 3 \
    "docker://${source_image}" \
    "docker-archive:${partial_file}:${archive_image}"

mv -f "$partial_file" "$output_file"
trap - EXIT

echo "Saved: $output_file"
