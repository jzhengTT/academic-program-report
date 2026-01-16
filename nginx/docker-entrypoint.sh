#!/bin/sh
# Docker entrypoint script for Nginx with multi-hostname support
# Converts comma-separated ADDITIONAL_HOSTNAMES to space-separated format
# and constructs SERVER_NAMES variable for nginx template substitution

set -e

# Convert comma-separated ADDITIONAL_HOSTNAMES to space-separated
if [ -n "$ADDITIONAL_HOSTNAMES" ]; then
    # Replace commas with spaces and trim whitespace
    ADDITIONAL_HOSTNAMES_SPACE=$(echo "$ADDITIONAL_HOSTNAMES" | tr ',' ' ' | xargs)
    # Combine FQDN with additional hostnames
    export SERVER_NAMES="${FQDN} ${ADDITIONAL_HOSTNAMES_SPACE}"
else
    # No additional hostnames, use only FQDN
    export SERVER_NAMES="${FQDN}"
fi

# Execute the default nginx entrypoint
exec /docker-entrypoint.sh "$@"
