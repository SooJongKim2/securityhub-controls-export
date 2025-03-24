# AWS Security Hub Control Exporter

[한국어 문서](README.ko.md)

## Project Description

This project is a tool that comprehensively collects security control information from AWS Security Hub and exports it to an Excel file. While AWS Security Hub provides various security standards and controls, not all necessary information is available through a single API. This tool utilizes multiple AWS APIs and crawls AWS documentation to gather comprehensive information about controls.

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
- **Remediation URL2**: AWS documentation URL generated based on control_id

### Information Collected via Web Crawling
- **Category**: AWS Security Hub documentation crawling
- **AWS Config rule**: AWS Security Hub documentation crawling
- **Schedule type**: AWS Security Hub documentation crawling
- **Remediation**: AWS Security Hub documentation crawling
- **Resource type**: AWS Security Hub documentation crawling

## Installation

### Prerequisites
- Python 3.7 or higher
- AWS CLI configured with appropriate IAM permissions

### AWS Permissions
The following permissions are required to run this tool:
- securityhub:DescribeStandards
- securityhub:ListSecurityControlDefinitions
- securityhub:GetSecurityControlDefinition

## Usage

### Git Clone & Package Installation
```bash
git clone https://github.com/SooJongKim2/securityhub-controls-export.git
cd securityhub-controls-export
pip install boto3 pandas openpyxl aiohttp beautifulsoup4 pytz colorama tqdm
```

### Basic Execution
```bash
python securityhub_controls_export.py
```

### Execute with All Standard Information
```bash
python securityhub_controls_export.py -wide
```

### Output
Upon completion, an Excel file named `securityhub_controls_%y%m%d_%H%M.xlsx` will be generated, containing comprehensive information about all Security Controls.

## Key Features
- Collects all security control information from AWS Security Hub
- Shows which security standards each control is implemented in
- Crawls additional information (categories, Config rules, resource types, etc.) from AWS documentation
- Exports information to Excel file
- Performance optimization through multiprocessing and async processing

## Notes
- Available security standards and controls may vary depending on AWS account and region
- Web crawling may be affected if AWS documentation structure changes
- Be mindful of API request limits as numerous API calls may occur

## License
This project is distributed under the MIT License.