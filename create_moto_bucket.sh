#!/bin/sh
set -eu

bucket_url="${S3_ENDPOINT_URL:?}/${S3_BUCKET_NAME:?}"
status=$(curl --silent --show-error --output /dev/null --write-out '%{http_code}' --head "$bucket_url")

case "$status" in
    200)
        echo "Moto bucket already exists: $S3_BUCKET_NAME"
        ;;
    404)
        curl --fail --silent --show-error --request PUT --header 'Content-Length: 0' "$bucket_url"
        echo "Created Moto bucket: $S3_BUCKET_NAME"
        ;;
    *)
        echo "Could not check Moto bucket $S3_BUCKET_NAME (HTTP $status)" >&2
        exit 1
        ;;
esac
