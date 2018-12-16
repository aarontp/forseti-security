#!/bin/bash
# Copyright 2018 The Forseti Security Authors. All rights reserved.
#
# Licensed under the Apache License, Versisn 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Usage
# (sudo if needed) docker exec ${CONTAINER_ID} /forseti-security/install/scripts/docker_entrypoint.sh ${BUCKET}

# UNDER DEVELOPMENT FOR PROOF OF CONCEPT PURPOSES ONLY
# This script serves as the entrypoint for starting Forseti server in a Docker container.
# Ref. https://docs.docker.com/engine/reference/builder/#entrypoint

# TODO Error handling in all functions

# Declare variables and set default values
BUCKET=
LOG_LEVEL=info
SERVICES="scanner model inventory explain notifier"
RUN_SERVER=true
RUN_CLIENT=false

# Note
# CLOUDSQLPROXY_SERVICE_HOST
# CLOUDSQLPROXY_SERVICE_PORT
# are environment variables set by k8s
# TODO process these as command line args if not running on k8s

download_configuration_files(){
    # Download config files from GCS
    # Use gsutil -DD debug flag if log level is debug
    DEBUG_FLAG=""
    if [ ${LOG_LEVEL} = "debug" ]; then
        DEBUG_FLAG="-DD"
    fi

    gsutil ${DEBUG_FLAG} cp ${BUCKET}/configs/forseti_conf_server.yaml /forseti-security/configs/forseti_conf_server.yaml
    gsutil ${DEBUG_FLAG} cp -r ${BUCKET}/rules /forseti-security/
}

start_server(){
    forseti_server \
    --endpoint "localhost:50051" \
    --forseti_db "mysql://root@${CLOUDSQLPROXY_SERVICE_HOST}:${CLOUDSQLPROXY_SERVICE_PORT}/forseti_security" \
    --services ${SERVICES} \
    --config_file_path "/forseti-security/configs/forseti_conf_server.yaml" \
    --log_level=${LOG_LEVEL} &
    #--enable_console_log
}

start_client(){
    #TODO
    echo "start_client() not implemented yet."
}

run_cron_job(){
    # Below cut and paste from run_forseti.sh
    # Ideally just call run_forseti.sh directly but for now its not quite right for us in GKE
    # due to the way it sources environment variables

    # Wait until the service is started
    sleep 10s

    # Set the output format to json
    forseti config format json

    # Purge inventory.
    # Use retention_days from configuration yaml file.
    forseti inventory purge

    # Run inventory command
    MODEL_NAME=$(/bin/date -u +%Y%m%dT%H%M%S)
    echo "Running Forseti inventory."
    forseti inventory create --import_as ${MODEL_NAME}
    echo "Finished running Forseti inventory."
    sleep 5s

    GET_MODEL_STATUS="forseti model get ${MODEL_NAME} | python -c \"import sys, json; print json.load(sys.stdin)['status']\""
    MODEL_STATUS=`eval $GET_MODEL_STATUS`

    if [ "$MODEL_STATUS" == "BROKEN" ]
        then
            echo "Model is broken, please contact discuss@forsetisecurity.org for support."
            exit
    fi

    # Run model command
    echo "Using model ${MODEL_NAME} to run scanner"
    forseti model use ${MODEL_NAME}
    # Sometimes there's a lag between when the model
    # successfully saves to the database.
    sleep 10s
    echo "Forseti config: $(forseti config show)"

    # Run scanner command
    echo "Running Forseti scanner."
    scanner_command=`forseti scanner run`
    scanner_index_id=`echo ${scanner_command} | grep -o -P '(?<=(ID: )).*(?=is created)'`
    echo "Finished running Forseti scanner."
    sleep 10s

    # Run notifier command
    echo "Running Forseti notifier."
    forseti notifier run
    echo "Finished running Forseti notifier."
    sleep 10s

    # Clean up the model tables
    echo "Cleaning up model tables"
    forseti model delete ${MODEL_NAME}

    # End cut and paste from run_forseti.sh
}

#error_exit()
#{
#	echo "$1" 1>&2
#	exit 1
#}

main(){

    if [ ${LOG_LEVEL}='debug' ]; then
        # Print commands to terminal
        set -x
    fi

    download_configuration_files

    # Run server or client; not both in same container
    if [ ${RUN_SERVER}="true" ]; then
        start_server
    elif [ ${RUN_CLIENT}="true" ]; then
        start_client
    fi

    if [ ${RUN_CRONJOB}="true" ]; then
        run_cron_job
    fi
}

# For now, just stop the script if an error occurs
set -e

# Read command line arguments
while [ "$1" != "" ]; do
    # Process next arg at position $1
    case $1 in
        --bucket )
            shift
            BUCKET=$1
            ;;
        --log_level )
            shift
            LOG_LEVEL=$1
            ;;
        --run_server )
            RUN_SERVER=true
            ;;
        --run_cronjob )
            RUN_CRONJOB=true
            ;;
        --run_client )
            RUN_CLIENT=true
            ;;
        --services )
            shift
            SERVICES=$1
            ;;
    esac
    shift # Move remaining args down 1 position
done

# Run this script
main
