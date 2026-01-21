#!/usr/bin/env python3
"""
LostFuzzer v2.0 - OpenAPI/Swagger Detection Module
===================================================
Detect and parse OpenAPI/Swagger documentation to extract all API endpoints.
"""

import sys
import json
import yaml
import requests
from pathlib import Path
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class OpenAPIDetector:
    """Detect and parse OpenAPI/Swagger specifications."""
    
    # Common OpenAPI/Swagger paths
    OPENAPI_PATHS = [
        '/swagger.json',
        '/swagger.yaml',
        '/swagger.yml',
        '/swagger-ui.html',
        '/swagger-ui/',
        '/swagger-resources',
        '/swagger-resources/configuration/ui',
        '/swagger-resources/configuration/security',
        '/openapi.json',
        '/openapi.yaml',
        '/openapi.yml',
        '/api-docs',
        '/api-docs.json',
        '/api-docs.yaml',
        '/v1/swagger.json',
        '/v2/swagger.json',
        '/v3/swagger.json',
        '/v1/api-docs',
        '/v2/api-docs',
        '/v3/api-docs',
        '/api/swagger.json',
        '/api/openapi.json',
        '/docs',
        '/docs/swagger.json',
        '/docs/openapi.json',
        '/redoc',
        '/.well-known/openapi.json',
        '/api/swagger-ui.html',
        '/swagger/v1/swagger.json',
        '/swagger/v2/swagger.json',
    ]
    
    # GraphQL endpoints
    GRAPHQL_PATHS = [
        '/graphql',
        '/graphiql',
        '/playground',
        '/altair',
        '/api/graphql',
        '/v1/graphql',
        '/graphql/console',
        '/graphql/playground',
    ]
    
    def __init__(self, output_dir: str = "."):
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, application/yaml, text/yaml, */*'
        })
        self.session.verify = False
        self.timeout = 10
    
    def detect_openapi(self, base_url: str) -> Optional[Dict]:
        """Detect and fetch OpenAPI specification for a target."""
        base_url = base_url.rstrip('/')
        
        for path in self.OPENAPI_PATHS:
            url = f"{base_url}{path}"
            try:
                response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    
                    # Try to parse as JSON
                    if 'json' in content_type or path.endswith('.json'):
                        try:
                            spec = response.json()
                            if self._is_valid_openapi(spec):
                                return {
                                    'url': url,
                                    'type': 'openapi',
                                    'spec': spec,
                                    'version': self._get_openapi_version(spec)
                                }
                        except json.JSONDecodeError:
                            pass
                    
                    # Try to parse as YAML
                    if 'yaml' in content_type or path.endswith(('.yaml', '.yml')):
                        try:
                            spec = yaml.safe_load(response.text)
                            if self._is_valid_openapi(spec):
                                return {
                                    'url': url,
                                    'type': 'openapi',
                                    'spec': spec,
                                    'version': self._get_openapi_version(spec)
                                }
                        except yaml.YAMLError:
                            pass
                    
                    # Try both for unknown content type
                    try:
                        spec = response.json()
                        if self._is_valid_openapi(spec):
                            return {
                                'url': url,
                                'type': 'openapi',
                                'spec': spec,
                                'version': self._get_openapi_version(spec)
                            }
                    except:
                        try:
                            spec = yaml.safe_load(response.text)
                            if self._is_valid_openapi(spec):
                                return {
                                    'url': url,
                                    'type': 'openapi',
                                    'spec': spec,
                                    'version': self._get_openapi_version(spec)
                                }
                        except:
                            pass
            except Exception:
                continue
        
        return None
    
    def detect_graphql(self, base_url: str) -> Optional[Dict]:
        """Detect GraphQL endpoint and check for introspection."""
        base_url = base_url.rstrip('/')
        
        introspection_query = {
            'query': '''
                query IntrospectionQuery {
                    __schema {
                        types {
                            name
                            kind
                            fields {
                                name
                            }
                        }
                        queryType { name }
                        mutationType { name }
                    }
                }
            '''
        }
        
        for path in self.GRAPHQL_PATHS:
            url = f"{base_url}{path}"
            try:
                # Check if endpoint exists
                response = self.session.post(
                    url,
                    json=introspection_query,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if 'data' in data and '__schema' in data.get('data', {}):
                            return {
                                'url': url,
                                'type': 'graphql',
                                'introspection_enabled': True,
                                'schema': data['data']['__schema']
                            }
                        elif 'errors' not in data:
                            return {
                                'url': url,
                                'type': 'graphql',
                                'introspection_enabled': False,
                                'schema': None
                            }
                    except:
                        pass
                
                # Also try GET request
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code in [200, 400]:  # 400 often means GraphQL endpoint without query
                    return {
                        'url': url,
                        'type': 'graphql',
                        'introspection_enabled': False,
                        'schema': None
                    }
                    
            except Exception:
                continue
        
        return None
    
    def _is_valid_openapi(self, spec: Dict) -> bool:
        """Check if spec is a valid OpenAPI/Swagger document."""
        if not isinstance(spec, dict):
            return False
        
        # Swagger 2.0
        if spec.get('swagger') and spec.get('paths'):
            return True
        
        # OpenAPI 3.x
        if spec.get('openapi') and spec.get('paths'):
            return True
        
        return False
    
    def _get_openapi_version(self, spec: Dict) -> str:
        """Get OpenAPI version from spec."""
        if spec.get('swagger'):
            return f"swagger-{spec['swagger']}"
        elif spec.get('openapi'):
            return f"openapi-{spec['openapi']}"
        return "unknown"
    
    def extract_endpoints(self, spec: Dict, base_url: str = "") -> List[Dict]:
        """Extract all endpoints from OpenAPI specification."""
        endpoints = []
        paths = spec.get('paths', {})
        
        # Get base path
        base_path = ""
        if spec.get('basePath'):
            base_path = spec['basePath']
        elif spec.get('servers'):
            server_url = spec['servers'][0].get('url', '')
            if server_url.startswith('/'):
                base_path = server_url
        
        for path, methods in paths.items():
            if not isinstance(methods, dict):
                continue
            
            full_path = f"{base_path}{path}".replace('//', '/')
            
            for method, details in methods.items():
                if method.lower() not in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                    continue
                
                endpoint = {
                    'path': full_path,
                    'method': method.upper(),
                    'url': urljoin(base_url, full_path) if base_url else full_path,
                    'summary': details.get('summary', ''),
                    'description': details.get('description', ''),
                    'tags': details.get('tags', []),
                    'parameters': [],
                    'security': details.get('security', []),
                    'deprecated': details.get('deprecated', False)
                }
                
                # Extract parameters
                for param in details.get('parameters', []):
                    endpoint['parameters'].append({
                        'name': param.get('name'),
                        'in': param.get('in'),
                        'required': param.get('required', False),
                        'type': param.get('type') or param.get('schema', {}).get('type', 'string')
                    })
                
                # Extract request body (OpenAPI 3.x)
                if 'requestBody' in details:
                    content = details['requestBody'].get('content', {})
                    for media_type, schema_info in content.items():
                        endpoint['request_body'] = {
                            'media_type': media_type,
                            'schema': schema_info.get('schema', {})
                        }
                        break
                
                endpoints.append(endpoint)
        
        return endpoints
    
    def extract_graphql_operations(self, schema: Dict) -> List[Dict]:
        """Extract operations from GraphQL introspection schema."""
        operations = []
        
        if not schema:
            return operations
        
        types = schema.get('types', [])
        query_type_name = schema.get('queryType', {}).get('name', 'Query')
        mutation_type_name = schema.get('mutationType', {}).get('name', 'Mutation')
        
        for type_info in types:
            type_name = type_info.get('name', '')
            
            if type_name == query_type_name:
                for field in type_info.get('fields', []) or []:
                    operations.append({
                        'type': 'query',
                        'name': field.get('name'),
                        'kind': 'QUERY'
                    })
            
            elif type_name == mutation_type_name:
                for field in type_info.get('fields', []) or []:
                    operations.append({
                        'type': 'mutation',
                        'name': field.get('name'),
                        'kind': 'MUTATION'
                    })
        
        return operations
    
    def scan_target(self, base_url: str) -> Dict:
        """Scan a single target for API documentation."""
        result = {
            'target': base_url,
            'openapi': None,
            'graphql': None,
            'endpoints': [],
            'graphql_operations': []
        }
        
        # Detect OpenAPI
        openapi_result = self.detect_openapi(base_url)
        if openapi_result:
            result['openapi'] = {
                'url': openapi_result['url'],
                'version': openapi_result['version']
            }
            result['endpoints'] = self.extract_endpoints(openapi_result['spec'], base_url)
        
        # Detect GraphQL
        graphql_result = self.detect_graphql(base_url)
        if graphql_result:
            result['graphql'] = {
                'url': graphql_result['url'],
                'introspection_enabled': graphql_result['introspection_enabled']
            }
            if graphql_result['schema']:
                result['graphql_operations'] = self.extract_graphql_operations(graphql_result['schema'])
        
        return result
    
    def run(self, targets_file: str, max_workers: int = 10) -> Dict:
        """Scan multiple targets for API documentation."""
        results = {
            'targets_scanned': 0,
            'openapi_found': 0,
            'graphql_found': 0,
            'total_endpoints': 0,
            'targets': [],
            'all_endpoints': []
        }
        
        # Read targets
        with open(targets_file, 'r') as f:
            targets = [line.strip() for line in f if line.strip()]
        
        print(f"[OPENAPI] Scanning {len(targets)} targets for API documentation...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.scan_target, target): target for target in targets}
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results['targets_scanned'] += 1
                    
                    if result['openapi'] or result['graphql']:
                        results['targets'].append(result)
                        
                        if result['openapi']:
                            results['openapi_found'] += 1
                        
                        if result['graphql']:
                            results['graphql_found'] += 1
                        
                        results['all_endpoints'].extend(result['endpoints'])
                except Exception as e:
                    pass
        
        results['total_endpoints'] = len(results['all_endpoints'])
        
        # Save results
        output_file = f"{self.output_dir}/openapi_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save endpoints as text file
        endpoints_file = f"{self.output_dir}/openapi_endpoints.txt"
        with open(endpoints_file, 'w') as f:
            for endpoint in results['all_endpoints']:
                f.write(f"{endpoint['method']} {endpoint['url']}\n")
        
        print(f"[OPENAPI] Targets scanned: {results['targets_scanned']}")
        print(f"[OPENAPI] OpenAPI specs found: {results['openapi_found']}")
        print(f"[OPENAPI] GraphQL endpoints found: {results['graphql_found']}")
        print(f"[OPENAPI] Total endpoints extracted: {results['total_endpoints']}")
        
        return results


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: openapi.py <targets_file> [output_dir]")
        sys.exit(1)
    
    targets_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    
    # Disable SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    detector = OpenAPIDetector(output_dir)
    results = detector.run(targets_file)
    
    print(f"\n[OPENAPI] Results saved to: {output_dir}/openapi_results.json")


if __name__ == "__main__":
    main()
