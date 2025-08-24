#!/usr/bin/env python3
"""
Simple test for command classification and timeout configuration
Tests core monitoring logic without external dependencies
"""
import sys
import os
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List

# Add client src to path
sys.path.append('client/src')

# Import only the core monitoring components
from smart_command_monitor import CommandType, TimeoutConfig, SmartCommandMonitor


def test_command_classification():
    """Test command classification functionality"""
    print("🔍 Testing Command Classification...")
    
    monitor = SmartCommandMonitor()
    
    test_commands = [
        ("ls -la", CommandType.QUICK_INFO),
        ("pwd", CommandType.QUICK_INFO),
        ("whoami", CommandType.QUICK_INFO),
        ("apt install python3", CommandType.PACKAGE_MANAGEMENT),
        ("yum install nginx", CommandType.PACKAGE_MANAGEMENT),
        ("pip install requests", CommandType.PACKAGE_MANAGEMENT),
        ("systemctl status nginx", CommandType.SYSTEM_SERVICE),
        ("service apache2 start", CommandType.SYSTEM_SERVICE),
        ("wget https://example.com/file.txt", CommandType.NETWORK_OPERATION),
        ("curl -O https://api.github.com/repos", CommandType.NETWORK_OPERATION),
        ("ssh user@host", CommandType.NETWORK_OPERATION),
        ("find /home -name '*.txt'", CommandType.FILE_OPERATION),
        ("cp file1.txt file2.txt", CommandType.FILE_OPERATION),
        ("chmod 755 script.sh", CommandType.FILE_OPERATION),
        ("make -j4", CommandType.COMPILATION),
        ("gcc -o program program.c", CommandType.COMPILATION),
        ("npm run build", CommandType.COMPILATION),
        ("sudo vim /etc/hosts", CommandType.INTERACTIVE),
        ("mysql -u root -p", CommandType.INTERACTIVE),
        ("python3 -i", CommandType.INTERACTIVE),
        ("mysterious_command --unknown", CommandType.UNKNOWN),
        ("nonexistent-tool --help", CommandType.UNKNOWN)
    ]
    
    correct = 0
    total = len(test_commands)
    
    for command, expected_type in test_commands:
        classified_type = monitor.classify_command(command)
        is_correct = classified_type == expected_type
        status = "✅" if is_correct else "❌"
        
        print(f"{status} '{command}'")
        print(f"   Classified as: {classified_type.value}")
        print(f"   Expected: {expected_type.value}")
        
        if is_correct:
            correct += 1
        print()
    
    print(f"📊 Classification accuracy: {correct}/{total} ({100*correct/total:.1f}%)")
    return correct == total


def test_timeout_configurations():
    """Test timeout configurations for different command types"""
    print("\n⏱️  Testing Timeout Configurations...")
    
    monitor = SmartCommandMonitor()
    
    test_scenarios = [
        ("ls -la", "Quick listing should have short timeout"),
        ("apt install large-package", "Package installation should have longer timeout"),
        ("systemctl status nginx", "Service status should have medium timeout"),
        ("wget https://example.com/large_file.zip", "Network download should have extended timeout"),
        ("make clean && make all", "Compilation should have longest timeout"),
        ("sudo nano /etc/config", "Interactive command should have extended timeout")
    ]
    
    all_valid = True
    
    for command, description in test_scenarios:
        config = monitor.get_timeout_config(command)
        cmd_type = monitor.classify_command(command)
        
        print(f"📋 {command}")
        print(f"   Type: {cmd_type.value}")
        print(f"   Description: {description}")
        print(f"   No output timeout: {config.no_output_timeout}s")
        print(f"   Max total timeout: {config.max_total_timeout}s")
        print(f"   CPU threshold: {config.cpu_threshold}%")
        print(f"   Check interval: {config.check_interval}s")
        
        # Validate timeout logic
        valid_config = (
            config.no_output_timeout > 0 and
            config.max_total_timeout > config.no_output_timeout and
            0 <= config.cpu_threshold <= 100 and
            config.check_interval > 0
        )
        
        if not valid_config:
            print("   ❌ Invalid timeout configuration!")
            all_valid = False
        else:
            print("   ✅ Configuration valid")
        print()
    
    return all_valid


def test_timeout_escalation():
    """Test timeout escalation logic"""
    print("\n📈 Testing Timeout Escalation Logic...")
    
    monitor = SmartCommandMonitor()
    
    # Test different command types have appropriate escalation
    escalation_tests = [
        (CommandType.QUICK_INFO, "Should have fast escalation"),
        (CommandType.PACKAGE_MANAGEMENT, "Should have patient escalation for downloads"),
        (CommandType.COMPILATION, "Should have very patient escalation for builds"),
        (CommandType.INTERACTIVE, "Should have extended patience for user input")
    ]
    
    for cmd_type, expectation in escalation_tests:
        config = monitor.TIMEOUT_CONFIGS[cmd_type]
        
        print(f"🎯 {cmd_type.value}")
        print(f"   Expectation: {expectation}")
        print(f"   No output → Alert: {config.no_output_timeout}s")
        print(f"   Max execution → Terminate: {config.max_total_timeout}s")
        print(f"   Escalation ratio: {config.max_total_timeout / config.no_output_timeout:.1f}x")
        
        # Validate escalation makes sense
        if cmd_type == CommandType.QUICK_INFO:
            assert config.no_output_timeout <= 15, "Quick commands should alert quickly"
            assert config.max_total_timeout <= 60, "Quick commands should terminate quickly"
        elif cmd_type == CommandType.COMPILATION:
            assert config.no_output_timeout >= 60, "Compilation should be patient"
            assert config.max_total_timeout >= 600, "Compilation should allow long execution"
        elif cmd_type == CommandType.INTERACTIVE:
            assert config.no_output_timeout >= 180, "Interactive should wait for user"
        
        print("   ✅ Escalation logic appropriate")
        print()
    
    return True


def test_command_patterns():
    """Test detection of specific command patterns"""
    print("\n🔍 Testing Command Pattern Detection...")
    
    monitor = SmartCommandMonitor()
    
    pattern_tests = [
        # Package management patterns
        ("apt update", CommandType.PACKAGE_MANAGEMENT),
        ("apt-get install vim", CommandType.PACKAGE_MANAGEMENT),
        ("yum update", CommandType.PACKAGE_MANAGEMENT),
        ("dnf install git", CommandType.PACKAGE_MANAGEMENT),
        ("pip install numpy", CommandType.PACKAGE_MANAGEMENT),
        ("npm install express", CommandType.PACKAGE_MANAGEMENT),
        
        # Service management patterns
        ("systemctl restart nginx", CommandType.SYSTEM_SERVICE),
        ("service apache2 reload", CommandType.SYSTEM_SERVICE),
        ("sudo systemctl enable docker", CommandType.SYSTEM_SERVICE),
        
        # Network patterns
        ("wget -r -np https://site.com/", CommandType.NETWORK_OPERATION),
        ("curl -X POST https://api.com/data", CommandType.NETWORK_OPERATION),
        ("ssh -p 2222 user@server", CommandType.NETWORK_OPERATION),
        ("scp file.txt user@host:/path/", CommandType.NETWORK_OPERATION),
        ("ping -c 4 google.com", CommandType.NETWORK_OPERATION),
        ("git clone https://github.com/repo.git", CommandType.NETWORK_OPERATION),
        
        # File operations
        ("find /var/log -name '*.log' -mtime +7", CommandType.FILE_OPERATION),
        ("tar -czf backup.tar.gz /home/user", CommandType.FILE_OPERATION),
        ("chmod -R 644 /var/www/html", CommandType.FILE_OPERATION),
        
        # Compilation
        ("make clean all", CommandType.COMPILATION),
        ("gcc -Wall -O2 -o app main.c utils.c", CommandType.COMPILATION),
        ("npm run build:production", CommandType.COMPILATION),
        ("cargo build --release", CommandType.COMPILATION),
        
        # Interactive
        ("sudo passwd user", CommandType.INTERACTIVE),
        ("mysql -u root -p database", CommandType.INTERACTIVE),
        ("python3 -i script.py", CommandType.INTERACTIVE),
        ("vim config.yaml", CommandType.INTERACTIVE)
    ]
    
    correct = 0
    total = len(pattern_tests)
    
    for command, expected_type in pattern_tests:
        detected_type = monitor.classify_command(command)
        is_correct = detected_type == expected_type
        
        if is_correct:
            correct += 1
            status = "✅"
        else:
            status = "❌"
            print(f"{status} '{command}' -> {detected_type.value} (expected {expected_type.value})")
    
    print(f"📊 Pattern detection accuracy: {correct}/{total} ({100*correct/total:.1f}%)")
    return correct >= total * 0.85  # Allow 85% accuracy


def test_edge_cases():
    """Test edge cases and unusual commands"""
    print("\n🔬 Testing Edge Cases...")
    
    monitor = SmartCommandMonitor()
    
    edge_cases = [
        ("", CommandType.UNKNOWN),  # Empty command
        ("   ", CommandType.UNKNOWN),  # Whitespace only
        ("sudo", CommandType.UNKNOWN),  # Incomplete command
        ("ls && apt install vim", CommandType.QUICK_INFO),  # Compound command (first wins)
        ("echo 'apt install vim'", CommandType.QUICK_INFO),  # Command in string
        ("cat file.txt | grep 'systemctl'", CommandType.QUICK_INFO),  # Piped command
        ("history | grep wget", CommandType.QUICK_INFO),  # History search
        ("alias ll='ls -la'", CommandType.UNKNOWN),  # Alias definition
        ("export PATH=$PATH:/usr/local/bin", CommandType.UNKNOWN),  # Environment variable
        ("# This is a comment", CommandType.UNKNOWN),  # Comment
        ("very-long-command-name-that-might-cause-issues --with --many --flags --and=values", CommandType.UNKNOWN)
    ]
    
    all_handled = True
    
    for command, expected_type in edge_cases:
        try:
            detected_type = monitor.classify_command(command)
            config = monitor.get_timeout_config(command)
            
            print(f"🧪 '{command}' -> {detected_type.value}")
            print(f"   Timeout: {config.no_output_timeout}s/{config.max_total_timeout}s")
            
        except Exception as e:
            print(f"❌ '{command}' caused error: {e}")
            all_handled = False
    
    return all_handled


def main():
    """Run all tests"""
    print("🧪 Smart Command Monitoring - Core Logic Tests")
    print("=" * 60)
    
    tests = [
        ("Command Classification", test_command_classification),
        ("Timeout Configurations", test_timeout_configurations),
        ("Timeout Escalation", test_timeout_escalation),
        ("Command Patterns", test_command_patterns),
        ("Edge Cases", test_edge_cases)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔄 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {status}")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"   {status} {test_name}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({100*passed/total:.1f}%)")
    
    if passed == total:
        print("\n🚀 All core logic tests passed! The smart monitoring system is ready.")
        print("\n📋 What this means:")
        print("   ✅ Commands are properly classified by type")
        print("   ✅ Timeout configurations are appropriate")
        print("   ✅ Escalation logic is sound")
        print("   ✅ Pattern detection works accurately")
        print("   ✅ Edge cases are handled gracefully")
        print("\n🔧 Next steps:")
        print("   1. Test with real hanging commands (manual)")
        print("   2. Verify WebSocket integration (requires backend)")
        print("   3. Test alternative command generation (requires LLM)")
        return 0
    else:
        print(f"\n❌ {total - passed} tests failed. Please review the implementation.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)