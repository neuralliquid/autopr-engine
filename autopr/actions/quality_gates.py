"""
AutoPR Action: Quality Gates
Validates fixes before committing, runs tests, checks quality metrics, and ensures compliance.
"""

import os
import subprocess
import json
import ast
import re
from typing import Dict, Any, Optional, List, Tuple
from pydantic import BaseModel

class QualityGateInputs(BaseModel):
    file_path: str
    original_content: str
    modified_content: str
    fix_type: str
    project_standards: Dict[str, Any] = {}
    run_tests: bool = True
    check_syntax: bool = True
    check_style: bool = True

class QualityGateOutputs(BaseModel):
    passed: bool
    warnings: List[str] = []
    errors: List[str] = []
    test_results: Dict[str, Any] = {}
    quality_score: float = 0.0
    recommendations: List[str] = []

class QualityGateValidator:
    def __init__(self):
        self.quality_checks = {
            'syntax': self._check_syntax,
            'style': self._check_style,
            'complexity': self._check_complexity,
            'security': self._check_security,
            'performance': self._check_performance,
            'tests': self._run_tests,
            'dependencies': self._check_dependencies,
            'accessibility': self._check_accessibility
        }
    
    def validate_fix(self, inputs: QualityGateInputs) -> QualityGateOutputs:
        """Run comprehensive quality validation on the fix."""
        warnings = []
        errors = []
        test_results = {}
        quality_scores = []
        recommendations = []
        
        # Write modified content to temporary file for testing
        temp_file = f"{inputs.file_path}.autopr_temp"
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(inputs.modified_content)
            
            # Run all quality checks
            for check_name, check_func in self.quality_checks.items():
                try:
                    result = check_func(temp_file, inputs)
                    
                    if result.get('warnings'):
                        warnings.extend(result['warnings'])
                    if result.get('errors'):
                        errors.extend(result['errors'])
                    if result.get('test_results'):
                        test_results[check_name] = result['test_results']
                    if result.get('quality_score') is not None:
                        quality_scores.append(result['quality_score'])
                    if result.get('recommendations'):
                        recommendations.extend(result['recommendations'])
                        
                except Exception as e:
                    warnings.append(f"{check_name} check failed: {str(e)}")
            
            # Calculate overall quality score
            overall_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.5
            
            # Determine if quality gate passes
            passed = len(errors) == 0 and overall_quality >= 0.7
            
            return QualityGateOutputs(
                passed=passed,
                warnings=warnings,
                errors=errors,
                test_results=test_results,
                quality_score=overall_quality,
                recommendations=recommendations
            )
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def _check_syntax(self, file_path: str, inputs: QualityGateInputs) -> Dict[str, Any]:
        """Check syntax validity of the modified file."""
        if not inputs.check_syntax:
            return {'quality_score': 1.0}
        
        errors = []
        file_ext = os.path.splitext(file_path)[1]
        
        try:
            if file_ext == '.py':
                # Python syntax check
                with open(file_path, 'r') as f:
                    ast.parse(f.read())
            
            elif file_ext in ['.js', '.ts', '.tsx', '.jsx']:
                # JavaScript/TypeScript syntax check using node
                result = subprocess.run(
                    ['node', '--check', file_path],
                    capture_output=True, text=True
                )
                if result.returncode != 0:
                    errors.append(f"Syntax error: {result.stderr}")
            
            elif file_ext in ['.json']:
                # JSON syntax check
                with open(file_path, 'r') as f:
                    json.load(f)
            
        except SyntaxError as e:
            errors.append(f"Syntax error: {str(e)}")
        except json.JSONDecodeError as e:
            errors.append(f"JSON syntax error: {str(e)}")
        except Exception as e:
            errors.append(f"Syntax check failed: {str(e)}")
        
        return {
            'errors': errors,
            'quality_score': 1.0 if not errors else 0.0
        }
    
    def _check_style(self, file_path: str, inputs: QualityGateInputs) -> Dict[str, Any]:
        """Check code style compliance."""
        if not inputs.check_style:
            return {'quality_score': 1.0}
        
        warnings = []
        recommendations = []
        file_ext = os.path.splitext(file_path)[1]
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Generic style checks
        lines = content.split('\n')
        
        # Check line length
        long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 120]
        if long_lines:
            warnings.append(f"Lines too long (>120 chars): {long_lines[:5]}")
        
        # Check trailing whitespace
        trailing_ws_lines = [i+1 for i, line in enumerate(lines) if line.rstrip() != line]
        if trailing_ws_lines:
            warnings.append(f"Trailing whitespace on lines: {trailing_ws_lines[:5]}")
        
        # Language-specific style checks
        if file_ext in ['.js', '.ts', '.tsx', '.jsx']:
            # Check for console.log in non-dev files
            if 'console.log' in content and 'dev' not in file_path.lower():
                warnings.append("Found console.log statements in production code")
            
            # Check for proper imports
            if re.search(r'import.*from [\'"][\.\/]', content):
                recommendations.append("Consider using absolute imports for better maintainability")
        
        quality_score = max(0.0, 1.0 - (len(warnings) * 0.1))
        
        return {
            'warnings': warnings,
            'recommendations': recommendations,
            'quality_score': quality_score
        }
    
    def _check_complexity(self, file_path: str, inputs: QualityGateInputs) -> Dict[str, Any]:
        """Check code complexity metrics."""
        warnings = []
        file_ext = os.path.splitext(file_path)[1]
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        if file_ext == '.py':
            # Count cyclomatic complexity for Python
            try:
                tree = ast.parse(content)
                complexity_score = self._calculate_python_complexity(tree)
                if complexity_score > 10:
                    warnings.append(f"High cyclomatic complexity: {complexity_score}")
            except:
                pass
        
        elif file_ext in ['.js', '.ts', '.tsx', '.jsx']:
            # Simple complexity check for JS/TS
            function_count = len(re.findall(r'function\s+\w+|=>\s*{|\w+\s*\([^)]*\)\s*{', content))
            if function_count > 20:
                warnings.append(f"File has many functions ({function_count}), consider splitting")
        
        # Check file size
        lines = len(content.split('\n'))
        if lines > 500:
            warnings.append(f"Large file ({lines} lines), consider refactoring")
        
        quality_score = max(0.0, 1.0 - (len(warnings) * 0.2))
        
        return {
            'warnings': warnings,
            'quality_score': quality_score
        }
    
    def _check_security(self, file_path: str, inputs: QualityGateInputs) -> Dict[str, Any]:
        """Check for potential security issues."""
        warnings = []
        file_ext = os.path.splitext(file_path)[1]
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Generic security checks
        security_patterns = [
            (r'password\s*=\s*[\'"][^\'"]+[\'"]', "Hardcoded password detected"),
            (r'api[_-]?key\s*=\s*[\'"][^\'"]+[\'"]', "Hardcoded API key detected"),
            (r'secret\s*=\s*[\'"][^\'"]+[\'"]', "Hardcoded secret detected"),
            (r'eval\s*\(', "Use of eval() detected - potential security risk"),
        ]
        
        for pattern, message in security_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                warnings.append(message)
        
        # JavaScript/TypeScript specific
        if file_ext in ['.js', '.ts', '.tsx', '.jsx']:
            if 'innerHTML' in content:
                warnings.append("Use of innerHTML detected - potential XSS risk")
            if 'dangerouslySetInnerHTML' in content:
                warnings.append("Use of dangerouslySetInnerHTML detected - ensure content is sanitized")
        
        quality_score = max(0.0, 1.0 - (len(warnings) * 0.3))
        
        return {
            'warnings': warnings,
            'quality_score': quality_score
        }
    
    def _check_performance(self, file_path: str, inputs: QualityGateInputs) -> Dict[str, Any]:
        """Check for potential performance issues."""
        warnings = []
        recommendations = []
        file_ext = os.path.splitext(file_path)[1]
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        if file_ext in ['.js', '.ts', '.tsx', '.jsx']:
            # Check for performance anti-patterns
            if re.search(r'useEffect\s*\([^,]*,\s*\[\]', content):
                recommendations.append("Consider using useMemo or useCallback for expensive operations")
            
            if content.count('useState') > 10:
                recommendations.append("Many useState hooks - consider useReducer for complex state")
            
            if 'map(' in content and 'filter(' in content:
                recommendations.append("Consider combining map and filter operations for better performance")
        
        quality_score = max(0.0, 1.0 - (len(warnings) * 0.1))
        
        return {
            'warnings': warnings,
            'recommendations': recommendations,
            'quality_score': quality_score
        }
    
    def _check_accessibility(self, file_path: str, inputs: QualityGateInputs) -> Dict[str, Any]:
        """Check for accessibility issues."""
        warnings = []
        file_ext = os.path.splitext(file_path)[1]
        
        if file_ext in ['.tsx', '.jsx']:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for accessibility patterns
            if '<img' in content and 'alt=' not in content:
                warnings.append("Image elements should have alt attributes")
            
            if '<button' in content and 'aria-label' not in content and 'aria-labelledby' not in content:
                # Only warn if button doesn't have visible text
                if re.search(r'<button[^>]*></button>', content):
                    warnings.append("Button elements should have accessible labels")
            
            if '<input' in content and 'id=' in content and '<label' not in content:
                warnings.append("Input elements should have associated labels")
        
        quality_score = max(0.0, 1.0 - (len(warnings) * 0.2))
        
        return {
            'warnings': warnings,
            'quality_score': quality_score
        }
    
    def _run_tests(self, file_path: str, inputs: QualityGateInputs) -> Dict[str, Any]:
        """Run relevant tests for the modified file."""
        if not inputs.run_tests:
            return {'quality_score': 1.0}
        
        test_results = {}
        warnings = []
        
        try:
            # Try to find and run tests related to this file
            test_file_patterns = [
                file_path.replace('.ts', '.test.ts'),
                file_path.replace('.tsx', '.test.tsx'),
                file_path.replace('.js', '.test.js'),
                file_path.replace('.jsx', '.test.jsx'),
                file_path.replace('/src/', '/tests/'),
                file_path.replace('.py', '_test.py')
            ]
            
            existing_test_files = [pattern for pattern in test_file_patterns if os.path.exists(pattern)]
            
            if existing_test_files:
                # Run the tests
                for test_file in existing_test_files:
                    result = self._run_test_file(test_file)
                    test_results[test_file] = result
            else:
                warnings.append("No tests found for this file")
                
        except Exception as e:
            warnings.append(f"Test execution failed: {str(e)}")
        
        # Calculate quality score based on test results
        if test_results:
            passed_tests = sum(1 for result in test_results.values() if result.get('passed', False))
            total_tests = len(test_results)
            quality_score = passed_tests / total_tests if total_tests > 0 else 0.5
        else:
            quality_score = 0.8  # Neutral score if no tests
        
        return {
            'warnings': warnings,
            'test_results': test_results,
            'quality_score': quality_score
        }
    
    def _run_test_file(self, test_file: str) -> Dict[str, Any]:
        """Run a specific test file."""
        try:
            # Determine test runner based on file type
            if test_file.endswith('.py'):
                result = subprocess.run(
                    ['python', '-m', 'pytest', test_file, '-v'],
                    capture_output=True, text=True, timeout=30
                )
            else:
                # Assume npm test for JS/TS files
                result = subprocess.run(
                    ['npm', 'test', '--', test_file],
                    capture_output=True, text=True, timeout=30
                )
            
            return {
                'passed': result.returncode == 0,
                'output': result.stdout,
                'errors': result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                'passed': False,
                'errors': 'Test execution timed out'
            }
        except Exception as e:
            return {
                'passed': False,
                'errors': str(e)
            }
    
    def _check_dependencies(self, file_path: str, inputs: QualityGateInputs) -> Dict[str, Any]:
        """Check for dependency-related issues."""
        warnings = []
        file_ext = os.path.splitext(file_path)[1]
        
        if file_ext in ['.js', '.ts', '.tsx', '.jsx']:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for unused imports (basic check)
            import_lines = re.findall(r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]', content)
            used_imports = []
            
            for imp in import_lines:
                # Simple check if import name appears elsewhere in the file
                import_name = imp.split('/')[-1].replace('-', '').replace('_', '')
                if import_name.lower() in content.lower():
                    used_imports.append(imp)
                else:
                    warnings.append(f"Potentially unused import: {imp}")
        
        quality_score = max(0.0, 1.0 - (len(warnings) * 0.1))
        
        return {
            'warnings': warnings,
            'quality_score': quality_score
        }
    
    def _calculate_python_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity for Python code."""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity

def quality_gates_action(inputs: QualityGateInputs) -> QualityGateOutputs:
    """Main action interface for quality gates validation."""
    validator = QualityGateValidator()
    return validator.validate_fix(inputs) 