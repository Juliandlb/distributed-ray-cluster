#!/bin/bash

# Azure Network Security Group Configuration Script
# This script helps configure Azure NSG to allow Docker Swarm ports

set -e

echo "🔧 Azure Network Security Group Configuration"
echo "==========================================="

echo ""
echo "📍 Current VM Public IP: $(curl -s ifconfig.me)"
echo ""

echo "📋 Required ports for Docker Swarm:"
echo "   - 2377/tcp: Docker Swarm management"
echo "   - 7946/tcp: Docker Swarm communication"
echo "   - 7946/udp: Docker Swarm communication"
echo "   - 4789/udp: Docker overlay network"
echo "   - 6379/tcp: Ray (already open)"
echo "   - 8265/tcp: Ray Dashboard (already open)"
echo ""

echo "🔧 To configure Azure NSG, you need to:"
echo ""
echo "1. Go to Azure Portal: https://portal.azure.com"
echo "2. Navigate to your VM's resource group"
echo "3. Find the Network Security Group (NSG) attached to your VM"
echo "4. Add the following inbound security rules:"
echo ""

echo "📝 Add these rules to your NSG:"
echo "--------------------------------"
echo "Rule 1:"
echo "  Name: DockerSwarm-Management"
echo "  Priority: 1000"
echo "  Port: 2377"
echo "  Protocol: TCP"
echo "  Source: Any"
echo "  Destination: Any"
echo "  Action: Allow"
echo ""

echo "Rule 2:"
echo "  Name: DockerSwarm-Communication-TCP"
echo "  Priority: 1001"
echo "  Port: 7946"
echo "  Protocol: TCP"
echo "  Source: Any"
echo "  Destination: Any"
echo "  Action: Allow"
echo ""

echo "Rule 3:"
echo "  Name: DockerSwarm-Communication-UDP"
echo "  Priority: 1002"
echo "  Port: 7946"
echo "  Protocol: UDP"
echo "  Source: Any"
echo "  Destination: Any"
echo "  Action: Allow"
echo ""

echo "Rule 4:"
echo "  Name: DockerOverlay-Network"
echo "  Priority: 1003"
echo "  Port: 4789"
echo "  Protocol: UDP"
echo "  Source: Any"
echo "  Destination: Any"
echo "  Action: Allow"
echo ""

echo "🔍 Alternative: Use Azure CLI (if you have it installed):"
echo "--------------------------------------------------------"
echo ""

# Get the resource group and VM name
echo "To find your resource group and VM name, run:"
echo "  az vm list --output table"
echo ""

echo "Then add the rules with Azure CLI:"
echo "  az network nsg rule create \\"
echo "    --resource-group <your-resource-group> \\"
echo "    --nsg-name <your-nsg-name> \\"
echo "    --name DockerSwarm-Management \\"
echo "    --protocol tcp \\"
echo "    --priority 1000 \\"
echo "    --destination-port-range 2377 \\"
echo "    --access Allow"
echo ""

echo "🔄 After adding the NSG rules:"
echo "1. Wait 1-2 minutes for the rules to propagate"
echo "2. Try the join script again on your laptop:"
echo "   ./join_swarm_worker.sh"
echo ""

echo "🚀 Quick Test:"
echo "From your laptop, test if port 2377 is now accessible:"
echo "  telnet 52.224.243.185 2377"
echo ""

echo "📊 Current accessible ports (should work):"
echo "  - Ray Dashboard: http://52.224.243.185:8265"
echo "  - Ray Port: 52.224.243.185:6379"
echo ""

echo "❓ If you can't configure the NSG, use the direct Ray connection:"
echo "   ./setup_laptop_worker.sh" 