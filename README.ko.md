# AWS Security Hub Control Exporter

## 프로젝트 설명

이 프로젝트는 AWS Security Hub의 보안 컨트롤(Security Controls) 정보를 종합적으로 수집하여 Excel 파일로 내보내는 도구입니다. AWS Security Hub는 다양한 보안 표준과 컨트롤을 제공하지만, 필요한 모든 정보가 단일 API를 통해 제공되지 않습니다. 이 도구는 여러 AWS API를 활용하고, AWS 문서를 크롤링하여 컨트롤에 대한 포괄적인 정보를 수집합니다.

## 데이터 수집 방법

각 컬럼별 정보 획득 방법:

### AWS API를 통해 수집하는 정보
- **Security Control ID**: `get_security_control_definition` API
- **Title**: `get_security_control_definition` API
- **Description**: `get_security_control_definition` API
- **Severity Rating**: `get_security_control_definition` API
- **Current Region Availability**: `get_security_control_definition` API
- **Remediation URL**: `get_security_control_definition` API
- **Parameters**: `get_security_control_definition` API의 ParameterDefinitions 필드
- **NbStandardsImplementedIn**: `describe_standards`와 `list_security_control_definitions` API 조합
- **ImplementedInStandards**: `describe_standards`와 `list_security_control_definitions` API 조합
- **각 표준별 구현 여부**: `describe_standards`와 `list_security_control_definitions` API 조합

### URL 생성 함수로 생성하는 정보
- **Remediation URL2**: control_id를 기반으로 AWS 문서 URL 생성

### 웹 크롤링을 통해 수집하는 정보
- **Category**: AWS Security Hub 문서 크롤링
- **AWS Config rule**: AWS Security Hub 문서 크롤링
- **Schedule type**: AWS Security Hub 문서 크롤링
- **Remediation**: AWS Security Hub 문서 크롤링
- **Resource type**: AWS Security Hub 문서 크롤링

## 설치 방법

### 필수 요구사항
- Python 3.7 이상
- AWS CLI 구성 및 적절한 IAM 권한

### AWS 권한 설정
이 도구를 실행하려면 다음 권한이 필요합니다:
- securityhub:DescribeStandards
- securityhub:ListSecurityControlDefinitions
- securityhub:GetSecurityControlDefinition

## 사용 방법

### git clone 및 패키지 설치
```bash
git clone https://github.com/SooJongKim2/securityhub-controls-export.git
pip install boto3 pandas openpyxl aiohttp beautifulsoup4 pytz colorama tqdm
```

### 기본 실행
```bash
python securityhub_controls_export.py
```

### 모든 표준 정보를 포함하여 실행
```bash
python securityhub_controls_export.py -wide
```

### 출력
실행이 완료되면 `securityhub_controls_%y%m%d_%H%M.xlsx` 형식의 Excel 파일이 생성됩니다. 이 파일에는 모든 Security Control에 대한 종합적인 정보가 포함되어 있습니다.

## 주요 기능
- AWS Security Hub의 모든 보안 컨트롤 정보 수집
- 각 컨트롤이 어떤 보안 표준에 구현되어 있는지 표시
- AWS 문서에서 추가 정보(카테고리, Config 규칙, 리소스 타입 등) 크롤링
- 정보를 Excel 파일로 내보내기
- 멀티프로세싱과 비동기 처리를 통한 성능 최적화

## 참고 사항
- AWS 계정과 리전에 따라 사용 가능한 보안 표준과 컨트롤이 다를 수 있습니다.
- 웹 크롤링은 AWS 문서 구조가 변경되면 영향을 받을 수 있습니다.
- 대량의 API 요청이 발생할 수 있으므로 API 요청 제한에 유의하세요.

## 라이선스
이 프로젝트는 MIT 라이선스 하에 배포됩니다.