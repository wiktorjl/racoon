#!/bin/bash
# LABEL: Clone a VM
# SUDO: true
# ARG: name "Enter the new VM name" "new-vm"
# ARG: template "Enter the template VM name" "template-dev-mini"
# ARG: hostname "Enter hostname" "new-vm"

# Arguments are passed as positional parameters
name="$1"
template="$2"
hostname="$3"

echo "---------------------------"
echo
echo "Cloning VM with these settings:"
echo "Name: $name"
echo "Template: $template"
echo "Hostname: $hostname"
echo "---------------------------"
newvm.sh "$template" "$name" "$hostname"
