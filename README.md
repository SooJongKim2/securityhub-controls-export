# AWS Security Hub Controls Export (Config Rule Map info)

[한국어 문서](README.ko.md)

## Project Description

This project is a script that comprehensively collects and exports AWS Security Hub's Security Controls information to an Excel file.

To effectively utilize Security Controls, which is the CSPM feature of AWS Security Hub, it is crucial to select appropriate Security Controls,
and this requires a process of collecting and analyzing detailed information about each Security Control.

Unfortunately, AWS provides Security Hub Security Controls information dispersed across multiple APIs.
Particularly, important data such as **Config Rule mapping information** and **remediation description** can only be found in AWS Docs.

This tool collects comprehensive information about security controls through various AWS API calls and AWS Docs crawling, and integrates them into a single Excel file.

## Key Features
- Collects all security control information from AWS Security Hub
- Shows which security standards each control is implemented in
- Crawls additional information (categories, Config rules, resource types, etc.) from AWS documentation
- Exports information to Excel file
- Performance optimization through multiprocessing and async processing

## Installation and Usage

### 1. Prerequisites
- Python 3.7 or higher
- AWS CLI configured with appropriate IAM permissions
- pip (Python package manager)

### 2. Environment Options
1. Local environment
2. AWS Cloud Shell (recommended)
   - No AWS credential configuration needed
   - Python and AWS CLI pre-installed
   - Free service included with AWS Console

### 3. AWS Permissions Required
Required IAM permissions:
- securityhub:DescribeStandards
- securityhub:ListSecurityControlDefinitions
- securityhub:GetSecurityControlDefinition

### 4. Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/SooJongKim2/securityhub-controls-export.git

# 2. Navigate to project directory
cd securityhub-controls-export

# 3. Install required packages
pip install boto3 pandas openpyxl aiohttp beautifulsoup4 pytz colorama tqdm
```

### 5. Execution Methods

```bash
# Basic execution
python securityhub_controls_export.py

# Execute with all standard information
python securityhub_controls_export.py -wide
```

### 6. Execution Results
- Generated filename: `securityhub_controls_%y%m%d_%H%M.xlsx`
- Included information: All Security Control related information

## Data Collection Methods

Information collection method for each column:

### Information Collected via AWS API
- **Security Control ID**: `get_security_control_definition` API
- **Title**: `get_security_control_definition` API
- **Description**: `get_security_control_definition` API
- **Severity Rating**: `get_security_control_definition` API
- **Current Region Availability**: `get_security_control_definition` API
- **Remediation URL**: `get_security_control_definition` API
- **Parameters**: `ParameterDefinitions` field from `get_security_control_definition` API
- **NbStandardsImplementedIn**: Combination of `describe_standards` and `list_security_control_definitions` APIs
- **ImplementedInStandards**: Combination of `describe_standards` and `list_security_control_definitions` APIs
- **Implementation Status per Standard**: Combination of `describe_standards` and `list_security_control_definitions` APIs

### Information Generated via URL Function
- **Remediation URL to Crawl**: AWS documentation URL generated based on control_id

### Information Collected via Web Crawling
- **Category**: AWS Security Hub documentation crawling
- **AWS Config rule**: AWS Security Hub documentation crawling
- **Schedule type**: AWS Security Hub documentation crawling
- **Remediation**: AWS Security Hub documentation crawling
- **Resource type**: AWS Security Hub documentation crawling

## Notes
- Available security standards and controls may vary depending on AWS account and region
- Web crawling may be affected if AWS documentation structure changes
- Be mindful of API request limits as numerous API calls may occur

## License
This project is distributed under the MIT License.