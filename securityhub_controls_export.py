
import boto3
import pandas as pd
from datetime import datetime
import time
import re
import pytz
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from multiprocessing import Pool, cpu_count
from functools import partial
import argparse
import colorama
from colorama import Fore, Style, Back
from tqdm import tqdm
import os

# Initialize colorama
colorama.init(autoreset=True)

def sort_security_control_id(control_id):
    """Sort security control IDs by name and number"""
    name = re.match(r'([A-Za-z]+)', control_id).group(1)
    number = int(re.search(r'(\d+)$', control_id).group(1))
    return (name, number)


def print_header(message):
    """Print a formatted header message"""
    terminal_width = os.get_terminal_size().columns
    print(f"\n{Back.BLUE}{Fore.WHITE}{Style.BRIGHT}{message.center(terminal_width)}{Style.RESET_ALL}")


def print_success(message):
    """Print a success message"""
    print(f"{Fore.GREEN}{Style.BRIGHT}✓ {message}{Style.RESET_ALL}")


def print_info(message):
    """Print an info message"""
    print(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")


def print_warning(message):
    """Print a warning message"""
    print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")


def print_error(message):
    """Print an error message"""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")


def get_standards_info():
    """Collect information about available standards and their controls"""
    print_header("COLLECTING STANDARDS INFORMATION")
    sh_client = boto3.client('securityhub')
    standards = []
    control_info = {}
    all_standards_names = set()
    
    # Get available standards
    print_info("Retrieving available standards...")
    paginator = sh_client.get_paginator('describe_standards')
    for page in paginator.paginate():
        standards.extend(page['Standards'])
    
    print_info(f"Found {len(standards)} standards")
    
    # Get controls for each standard and collect info
    print_info("Retrieving controls for each standard...")
    for standard in tqdm(standards, desc="Processing standards"):
        standard_arn = standard['StandardsArn']
        standard_name = standard['Name']
        all_standards_names.add(standard_name)
        
        paginator = sh_client.get_paginator('list_security_control_definitions')
        for page in paginator.paginate(StandardsArn=standard_arn):
            for control in page['SecurityControlDefinitions']:
                control_id = control['SecurityControlId']
                if control_id not in control_info:
                    control_info[control_id] = {
                        'count': 0,
                        'standards': set()
                    }
                control_info[control_id]['count'] += 1
                control_info[control_id]['standards'].add(standard_name)
    
    print_success(f"Collected information for {len(control_info)} controls across {len(all_standards_names)} standards")
    return control_info, all_standards_names


def process_control(control, control_info, all_standards_names, counter):
    """Process a single security control and extract its details"""
    try:
        security_hub = boto3.client('securityhub')
        control_id = control['SecurityControlId']
        
        detail = security_hub.get_security_control_definition(
            SecurityControlId=control_id
        )
        
        control_detail = detail['SecurityControlDefinition']
        
        # Get standards info for this control
        standards_count = control_info.get(control_id, {'count': 0, 'standards': set()})['count']
        standards_list = control_info.get(control_id, {'standards': set()})['standards']
        standards_str = ', '.join(sorted(standards_list)) if standards_list else 'N/A'
        
        # Extract parameter information
        parameters = control_detail.get('ParameterDefinitions', {})
        parameter_info = ""
        for param_name, param_details in parameters.items():
            config_options = param_details.get('ConfigurationOptions', {})
            parameter_info += f"Parameter: {param_name}\n"
            parameter_info += f"Description: {param_details.get('Description', 'N/A')}\n"
            for option_type, option_values in config_options.items():
                parameter_info += f"Type: {option_type}\n"
                parameter_info += f"Default Value: {option_values.get('DefaultValue', 'N/A')}\n"
                parameter_info += f"Min: {option_values.get('Min', 'N/A')}\n"
                parameter_info += f"Max: {option_values.get('Max', 'N/A')}\n"
            parameter_info += "---\n"
        
        result = {
            'Security Control ID': control_detail['SecurityControlId'],
            'Title': control_detail['Title'],
            'Description': control_detail['Description'],
            'Severity Rating': control_detail['SeverityRating'],
            'Current Region Availability': control_detail['CurrentRegionAvailability'],
            'Remediation URL': control_detail.get('RemediationUrl', 'N/A'),
            'Parameters': parameter_info,
            'NbStandardsImplementedIn': standards_count,
            'ImplementedInStandards': standards_str
        }
        
        # Add columns for each standard
        for standard_name in all_standards_names:
            result[f'Implemented in {standard_name}'] = standard_name in standards_list
        
        return result
        
    except Exception as control_error:
        print_error(f"Error processing control {control['SecurityControlId']}: {str(control_error)}")
        return None


async def create_remediation_url(control_id):
    """Create the documentation URL for a security control"""
    service, number = control_id.split('.')
    base_url = "https://docs.aws.amazon.com/securityhub/latest/userguide"
    return f"{base_url}/{service.lower()}-controls.html#{service.lower()}-{number}"


def extract_config_rule(control_section):
    """Extract Config rule information from a SecurityHub control section"""
    def find_next_sibling_with_substring(element, element_type, substrings):
        """Helper function to find the next sibling element containing specific substrings"""
        def detect_substring(tag):
            return tag.name == element_type and any(s in tag.text for s in substrings)
        
        result = element.find_next_sibling(detect_substring)
        if not result:
            return None, ""
            
        result_text = result.text
        for string in substrings:
            result_text = result_text.replace(string, '')
        result_text = result_text.strip()
        
        return result, result_text

    # Patterns that might contain Config rule
    config_rule_patterns = [
        "AWS Config rule:",
        "AWS Config Rule:",
        "AWS Configrule:"
    ]

    # Find Config rule info in the next sibling element
    element, element_text = find_next_sibling_with_substring(
        element=control_section,
        element_type='p',
        substrings=config_rule_patterns
    )

    if not element:
        return None

    # Handle "None (custom Security Hub rule)" case
    if "None (custom Security Hub rule)" in element.text:
        return "None (custom Security Hub rule)"

    # If Config rule has a link
    config_rule_link = element.find('a')
    if config_rule_link:
        rule_text = config_rule_link.text.strip()
        
        # Check for custom Security Hub rule
        if "(custom Security Hub rule)" in element.text:
            return f"{rule_text} (custom Security Hub rule)"
        return rule_text

    # If Config rule is in a code tag
    code_tag = element.find('code')
    if code_tag:
        rule_text = code_tag.text.strip()
        
        # Check for custom Security Hub rule
        if "(custom Security Hub rule)" in element.text:
            return f"{rule_text} (custom Security Hub rule)"
        return rule_text

    # If Config rule exists as plain text
    clean_text = element_text.strip()
    if clean_text:
        # Check for custom Security Hub rule
        if "(custom Security Hub rule)" in element.text:
            return f"{clean_text} (custom Security Hub rule)"
        return clean_text

    return None


async def process_control_web(session, index, row, df, progress_bar):
    """Extract additional information about a control from AWS documentation"""
    control_id = row['Security Control ID']
    url = row['Remediation URL to Crawl']
    
    try:
        async with session.get(url) as response:
            html = await response.text()
            
        soup = BeautifulSoup(html, 'html.parser')
        control_section = soup.find('h2', id=control_id.lower().replace('.', '-'))
        
        if control_section:
            # Extract Category
            category_element = control_section.find_next('b', string='Category:')
            if category_element:
                category = category_element.next_sibling.strip()
                df.at[index, 'Category'] = category
            
            # Extract Resource type
            resource_element = control_section.find_next('b', string='Resource type:')
            if resource_element:
                code_element = resource_element.find_next('code')
                if code_element:
                    resource_type = code_element.text.strip()
                    df.at[index, 'Resource type'] = resource_type
            
            # Extract AWS Config rule
            config_rule = extract_config_rule(control_section)
            if config_rule:
                df.at[index, 'AWS Config rule'] = config_rule
            
            # Extract Schedule type
            schedule_element = control_section.find_next('b', string='Schedule type:')
            if schedule_element:
                schedule = schedule_element.next_sibling.strip()
                df.at[index, 'Schedule type'] = schedule
            
            # Extract Remediation
            remediation_header = control_section.find_next(['h3'], id=lambda x: x and 'remediation' in x.lower())
            if remediation_header:
                remediation_text = []
                current = remediation_header.find_next_sibling()

                while current and not (current.name == 'h2' or current.name == 'h3'):
                    if current.name in ['p', 'div', 'ul', 'ol']:
                        if current.name in ['ul', 'ol']:
                            list_items = current.find_all('li')
                            for item in list_items:
                                text = item.get_text().strip()
                                if text:
                                    text = re.sub(r'\s+', ' ', text)
                                    remediation_text.append(text)
                        else:
                            text = current.get_text().strip()
                            if text:
                                text = re.sub(r'\s+', ' ', text)
                                remediation_text.append(text)
                    current = current.find_next_sibling()

                remediation_text = [text for text in remediation_text if text]
                combined_text = ' '.join(remediation_text)
                combined_text = re.sub(r'\s+', ' ', combined_text)
                df.at[index, 'Remediation'] = combined_text
        
        progress_bar.update(1)
        
    except Exception as e:
        print_error(f"Error processing web info for {control_id}: {str(e)}")
        progress_bar.update(1)


async def crawl_web_data(df):
    """Crawl AWS documentation to extract additional control information"""
    print_header("WEB DATA CRAWLING")
    
    # Create additional columns
    print_info("Creating remediation URLs...")
    df['Remediation URL to Crawl'] = await asyncio.gather(*[create_remediation_url(control_id) for control_id in df['Security Control ID']])
    df['Category'] = ''
    df['Resource type'] = ''
    df['AWS Config rule'] = ''
    df['Schedule type'] = ''
    df['Remediation'] = ''    
    
    print_info("Starting web crawling...")
    async with aiohttp.ClientSession() as session:
        with tqdm(total=len(df), desc="Crawling web data", unit="control") as progress_bar:
            tasks = [process_control_web(session, index, row, df, progress_bar) for index, row in df.iterrows()]
            await asyncio.gather(*tasks)
    
    print_success("Web data crawling completed")
    return df


async def main(wide_format=False):
    """Main function to export all security controls to Excel"""
    start_time = time.time()
    pool = None
    try:
        print_header("AWS SECURITY HUB CONTROLS EXPORTER")
        print_info(f"Starting export process at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        security_hub = boto3.client('securityhub')
        
        # Get control info first
        control_info, all_standards_names = get_standards_info()
        
        # Get Security Control Definitions
        print_header("COLLECTING SECURITY CONTROL DEFINITIONS")
        controls = []
        paginator = security_hub.get_paginator('list_security_control_definitions')
        
        for page in paginator.paginate():
            controls.extend(page['SecurityControlDefinitions'])
        
        print_info(f"Found {len(controls)} security controls")
        
        # Setup multiprocessing with system CPU count
        num_processes = cpu_count()
        print_info(f"Total CPU cores: {num_processes}")
        print_info(f"Number of processes for multiprocessing: {num_processes}")
        pool = Pool(processes=num_processes)
        print(f"{Fore.MAGENTA}Multiprocessing setup complete: Running parallel processing with {num_processes} cores{Style.RESET_ALL}")
        counter = 0  # Define counter variable to track progress

        # Run parallel processing
        print_info("Processing controls in parallel...")
        with tqdm(total=len(controls), desc="Processing controls", unit="control") as pbar:
            results = []
            for result in pool.imap(partial(process_control, control_info=control_info, all_standards_names=all_standards_names, counter=counter), controls):
                results.append(result)
                pbar.update(1)
        
        # Filter valid results
        controls_data = [result for result in results if result is not None]
        
        print_success(f"Successfully processed {len(controls_data)} controls")
        
        # Create DataFrame
        df = pd.DataFrame(controls_data)      
        
        # Perform web crawling for additional information
        df = await crawl_web_data(df)
        
        # Sort by Security Control ID
        print_info("Sorting controls by ID...")
        df = df.sort_values(by='Security Control ID', 
                          key=lambda x: pd.Series(x).map(sort_security_control_id))
        
        # Include timestamp in filename
        current_time = datetime.now().strftime('%y%m%d_%H%M')
        filename = f'securityhub_controls_{current_time}.xlsx'
        
        print_header("CREATING EXCEL FILE")
        # Save to Excel file
        writer = pd.ExcelWriter(filename, engine='openpyxl')
        
        # Configure column width based on format
        if not wide_format:
            print_info("Using standard format (excluding standard-specific columns)")
            # Basic format - exclude standard-specific columns
            standard_columns = [col for col in df.columns if col.startswith('Implemented in ')]
            df_export = df.drop(columns=standard_columns)
        else:
            print_info("Using wide format (including standard-specific columns)")
            # Extended format - include all columns
            df_export = df
            
        df_export.to_excel(writer, index=False, sheet_name='Security Controls')
        worksheet = writer.sheets['Security Controls']
        
        # Adjust column widths
        print_info("Adjusting column widths...")
        for idx, col in enumerate(df_export.columns):
            max_length = max(
                df_export[col].astype(str).apply(len).max(),
                len(col)
            )
            worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 100)
        
        writer.close()
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print_header("EXPORT COMPLETED")
        print_success(f"Successfully exported {len(controls_data)} security controls to {filename}")
        print_success(f"Total execution time: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
        
    except Exception as e:
        print_error(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if pool is not None:
            pool.close()
            pool.join()


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Export AWS Security Hub controls to Excel')
    parser.add_argument('-wide', action='store_true', 
                        help='Include additional columns for each standard implementation')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    asyncio.run(main(wide_format=args.wide))