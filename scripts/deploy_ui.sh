#!/usr/bin/env bash
set -euo pipefail

source scripts/utils.sh

export NODE_IP=$(get_main_ip)
export UI_PORT=${UI_PORT:-6008}
export KUBECONFIG=${KUBECONFIG:-$HOME/.kube/config}
export CONTAINER_COMMAND=${CONTAINER_COMMAND:-podman}
export UI_DEPLOY_FILE=build/ui_deploy.yaml
export UI_SERVICE_NAME=ocp-metal-ui
export NO_UI=${NO_UI:-n}
export NAMESPACE=${NAMESPACE:-assisted-installer}
if [ "${CONTAINER_COMMAND}" = "podman" ]; then
    export PODMAN_FLAGS="--pull=always"
else
    export PODMAN_FLAGS=""
fi

if [ "${NO_UI}" != "n" ]; then
    exit 0
fi

mkdir -p build
#In case deploy tag is empty use latest
[[ -z "${DEPLOY_TAG}" ]] && export DEPLOY_TAG=latest

print_log "Starting ui"

${CONTAINER_COMMAND} pull quay.io/ocpmetal/ocp-metal-ui:latest
${CONTAINER_COMMAND} run ${PODMAN_FLAGS} --rm quay.io/ocpmetal/ocp-metal-ui:latest /deploy/deploy_config.sh -u http://assisted-service.${NAMESPACE}.svc.cluster.local:8090 -i quay.io/ocpmetal/ocp-metal-ui:${DEPLOY_TAG} -n ${NAMESPACE} >${UI_DEPLOY_FILE}
kubectl --kubeconfig=${KUBECONFIG} apply -f ${UI_DEPLOY_FILE}

print_log "Wait till ui api is ready"
wait_for_url_and_run "$(minikube service ${UI_SERVICE_NAME} -n ${NAMESPACE} --url)" "echo \"waiting for ${UI_SERVICE_NAME}\""

print_log "Starting port forwarding for deployment/${UI_SERVICE_NAME}"
wait_for_url_and_run "http://${NODE_IP}:${UI_PORT}" "spawn_port_forwarding_command ${UI_SERVICE_NAME} ${UI_PORT}"
print_log "OCP METAL UI can be reached at http://${NODE_IP}:${UI_PORT}"
print_log "Done"
