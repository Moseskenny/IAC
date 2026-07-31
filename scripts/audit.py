import boto3
import json

def audit_security_groups():
    # Uses environment variables set by GitHub actions for auth
    ec2 = boto3.client('ec2', region_name='ap-south-1')
    response = ec2.describe_security_groups()
    
    findings = []
    for sg in response['SecurityGroups']:
        for permission in sg['IpPermissions']:
            # Check for overly permissive SSH access
            if permission.get('FromPort') == 22:
                for ip_range in permission.get('IpRanges', []):
                    if ip_range['CidrIp'] == '0.0.0.0/0':
                        findings.append({
                            "type": "VULNERABILITY",
                            "resource_id": sg['GroupId'],
                            "issue": "SSH Port 22 is open to 0.0.0.0/0",
                            "severity": "HIGH"
                        })
    return findings

if __name__ == "__main__":
    print("Initiating Infrastructure Security Audit...")
    try:
        report = audit_security_groups()
        print(json.dumps({"audit_findings": report}, indent=4))
        
        if report:
            print(f"\n[WARNING] Found {len(report)} security misconfiguration(s).")
        else:
            print("\n[SUCCESS] Infrastructure meets security baselines.")
            
    except Exception as e:
        print(f"AWS Connection Error: {str(e)}")