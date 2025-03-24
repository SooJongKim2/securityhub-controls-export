# AWS Security Hub Control Exporter

## 프로젝트 설명

이 프로젝트는 AWS Security Hub의 Security Controls 정보를 종합적으로 수집하여 Excel 파일로 추출하는 스크립트입니다.

AWS Security Hub의 CSPM 기능인 Security Controls활용을 위해서는 적절한 Security Controls을 선택하는 것이 중요하며,
이를 위해 각 Security Controls의 상세 정보를 수집하고 분석하는 과정이 필수적입니다.

안타깝게도 AWS에서는 Security Hub Security Controls 관련 정보를 여러 API를 통해 분산하여 제공하고 있습니다.
특히 **Config Rule 맵핑 정보**나 필요한 **조치 설명 정보**와 같은 중요 데이터는 AWS Docs에서만 확인이 가능합니다.

이 도구는 다양한 AWS API 호출과 AWS Docs 크롤링을 통해 보안 컨트롤에 대한 포괄적인 정보를 수집하고, 이를 하나의 Excel 파일로 통합하여 제공합니다.

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
- **Remediation URL to Crawl**: control_id를 기반으로 AWS 문서 URL 생성

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

### 실행 환경 옵션
이 도구는 다음 환경에서 실행할 수 있습니다:
1. 로컬 환경
2. AWS Cloud Shell (빠른 설정을 위해 권장)
   - AWS 자격 증명 구성이 필요 없음
   - Python과 AWS CLI가 사전 설치되어 있음
   - AWS 콘솔에 포함된 무료 서비스

### AWS 권한 설정
이 도구를 실행하려면 다음 권한이 필요합니다:
- securityhub:DescribeStandards
- securityhub:ListSecurityControlDefinitions
- securityhub:GetSecurityControlDefinition

## 사용 방법

### git clone 및 패키지 설치
```bash
git clone https://github.com/SooJongKim2/securityhub-controls-export.git
cd securityhub-controls-export
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