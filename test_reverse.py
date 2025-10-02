import os
import subprocess
import shutil
from pathlib import Path
import hashlib
import binascii

class ReverseEngineeringTester:
    def __init__(self):
        self.results = {}
        self.tools_status = {}
        
    def check_tool(self, tool_name, command):
        try:
            subprocess.run(command, capture_output=True)
            self.tools_status[tool_name] = True
            return True
        except Exception:
            self.tools_status[tool_name] = False
            return False

    def calculate_file_hash(self, file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def extract_strings(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            strings = []
            current_string = ''
            
            for byte in content:
                if 32 <= byte <= 126:  # Printable ASCII characters
                    current_string += chr(byte)
                elif current_string:
                    if len(current_string) >= 4:  # Chỉ lưu chuỗi có độ dài >= 4
                        strings.append(current_string)
                    current_string = ''
            
            return strings
        except Exception as e:
            return [f"Error extracting strings: {str(e)}"]

    def test_pyinstaller_extraction(self, file_path):
        """Test khả năng extract PyInstaller executable"""
        try:
            output_dir = Path(file_path).parent / "extracted_pyinstaller"
            if output_dir.exists():
                shutil.rmtree(output_dir)
            output_dir.mkdir()
            
            # Thử extract với pyinstxtractor
            result = subprocess.run(
                ["python", "-m", "pyinstxtractor", file_path],
                capture_output=True,
                text=True
            )
            
            extracted_files = list(output_dir.rglob("*"))
            return {
                "success": result.returncode == 0,
                "files_found": len(extracted_files),
                "python_files": len([f for f in extracted_files if f.suffix == '.pyc']),
                "output": result.stdout
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def test_nuitka_analysis(self, file_path):
        """Phân tích file được compile bởi Nuitka"""
        try:
            strings = self.extract_strings(file_path)
            interesting_strings = [s for s in strings if any(x in s.lower() for x in 
                ['python', 'import', 'class', 'def', 'secret', 'password'])]
            
            # Thử tìm symbols với nm (nếu có)
            try:
                symbols = subprocess.run(
                    ["nm", file_path],
                    capture_output=True,
                    text=True
                ).stdout
            except:
                symbols = "Tool 'nm' not available"
            
            return {
                "strings_found": len(strings),
                "interesting_strings": len(interesting_strings),
                "examples": interesting_strings[:10],
                "symbols": symbols
            }
        except Exception as e:
            return {"error": str(e)}

    def test_pyarmor_decompilation(self, file_path):
        """Test khả năng decompile file được bảo vệ bởi PyArmor"""
        try:
            # Thử với uncompyle6
            uncompyle_result = subprocess.run(
                ["python", "-m", "uncompyle6", file_path],
                capture_output=True,
                text=True
            )
            
            # Thử với decompyle3
            decompyle3_result = subprocess.run(
                ["python", "-m", "decompyle3", file_path],
                capture_output=True,
                text=True
            )
            
            return {
                "uncompyle6": {
                    "success": uncompyle_result.returncode == 0,
                    "output": uncompyle_result.stdout
                },
                "decompyle3": {
                    "success": decompyle3_result.returncode == 0,
                    "output": decompyle3_result.stdout
                }
            }
        except Exception as e:
            return {"error": str(e)}

    def check_debug_protection(self, file_path):
        """Kiểm tra các biện pháp bảo vệ chống debug"""
        try:
            strings = self.extract_strings(file_path)
            debug_indicators = [
                'IsDebuggerPresent',
                'CheckRemoteDebuggerPresent',
                'OutputDebugString',
                'debugger',
                'anti-debug'
            ]
            found_indicators = [s for s in strings if any(i.lower() in s.lower() for i in debug_indicators)]
            
            return {
                "has_debug_protection": len(found_indicators) > 0,
                "protection_methods": found_indicators
            }
        except Exception as e:
            return {"error": str(e)}

    def test_binary(self, file_path):
        """Chạy tất cả các test trên một file binary"""
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        file_info = {
            "file_size": os.path.getsize(file_path),
            "file_hash": self.calculate_file_hash(file_path)
        }
        
        results = {
            "file_info": file_info,
            "pyinstaller_test": self.test_pyinstaller_extraction(file_path),
            "nuitka_analysis": self.test_nuitka_analysis(file_path),
            "pyarmor_test": self.test_pyarmor_decompilation(file_path),
            "debug_protection": self.check_debug_protection(file_path)
        }
        
        self.results[file_path] = results
        return results

    def print_report(self, results):
        """In báo cáo chi tiết về kết quả test"""
        print("\n=== Reverse Engineering Test Report ===")
        print("\nFile Information:")
        print(f"Size: {results['file_info']['file_size']} bytes")
        print(f"SHA256: {results['file_info']['file_hash']}")
        
        print("\nPyInstaller Extraction Test:")
        pi_test = results['pyinstaller_test']
        if 'error' in pi_test:
            print(f"Error: {pi_test['error']}")
        else:
            print(f"Extraction successful: {pi_test.get('success', False)}")
            print(f"Files found: {pi_test.get('files_found', 0)}")
            print(f"Python files found: {pi_test.get('python_files', 0)}")
        
        print("\nNuitka Analysis:")
        na_test = results['nuitka_analysis']
        if 'error' in na_test:
            print(f"Error: {na_test['error']}")
        else:
            print(f"Strings found: {na_test.get('strings_found', 0)}")
            print(f"Interesting strings: {na_test.get('interesting_strings', 0)}")
            print("\nExample strings found:")
            for example in na_test.get('examples', []):
                print(f"  - {example}")
        
        print("\nPyArmor Decompilation Test:")
        pa_test = results['pyarmor_test']
        if 'error' in pa_test:
            print(f"Error: {pa_test['error']}")
        else:
            print("Uncompyle6 success:", pa_test.get('uncompyle6', {}).get('success', False))
            print("Decompyle3 success:", pa_test.get('decompyle3', {}).get('success', False))
        
        print("\nDebug Protection Analysis:")
        dp_test = results['debug_protection']
        if 'error' in dp_test:
            print(f"Error: {dp_test['error']}")
        else:
            print(f"Has debug protection: {dp_test.get('has_debug_protection', False)}")
            if dp_test.get('protection_methods', []):
                print("\nProtection methods found:")
                for method in dp_test['protection_methods']:
                    print(f"  - {method}")

def main():
    tester = ReverseEngineeringTester()
    
    # Test các file trong các thư mục khác nhau
    test_files = [
        "PyInstaller/dist/main.exe",
        "Nuitka/main.exe",
        "PyArmor/dist/main.py"
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"\nTesting {file_path}...")
            results = tester.test_binary(file_path)
            tester.print_report(results)
        else:
            print(f"\nSkipping {file_path} - file not found")

if __name__ == "__main__":
    main()