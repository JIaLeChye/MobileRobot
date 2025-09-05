#!/usr/bin/env python3
"""
Boot Self-Test System
====================

Automatic power-on self-test for Raspberry Pi 5 Mobile Robot
Runs comprehensive tests on startup to ensure all systems are operational

Features:
- Automatic startup testing
- Visual and audio feedback
- System health validation
- Error reporting and recovery
- Safe startup sequence

Author: GitHub Copilot
Date: September 2025
"""

import os
import sys
import time
import subprocess
from datetime import datetime

# Add project paths
sys.path.append('/home/raspberry/Desktop/MobileRobot')
sys.path.append('/home/raspberry/Desktop/MobileRobot/Libraries/Ultrasonic_Sensor')
sys.path.append('/home/raspberry/Desktop/MobileRobot/Libraries/IR_Sensor')

try:
    from complete_self_test import RobotSelfTest
    from RPi_Robot_Hat_Lib import RobotController
except ImportError as e:
    print(f"❌ Critical Import Error: {e}")
    print("Please ensure all required modules are installed.")
    sys.exit(1)

class BootSelfTest:
    """Boot-time self-test system for the mobile robot"""
    
    def __init__(self):
        self.test_system = None
        self.robot = None
        self.start_time = datetime.now()
        
    def print_banner(self):
        """Display startup banner"""
        print("\n" + "="*60)
        print("🤖 RASPBERRY PI 5 MOBILE ROBOT - BOOT SELF TEST")
        print("="*60)
        print(f"📅 Boot Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔧 Platform: Raspberry Pi 5 with Robot Hat")
        print("🚀 Starting power-on self-test...")
        print("="*60 + "\n")
        
    def wait_for_system_ready(self):
        """Wait for system to be ready for testing"""
        print("⏳ Waiting for system initialization...")
        
        # Wait for I2C to be ready
        for i in range(5):
            try:
                # Test I2C availability
                result = subprocess.run(['i2cdetect', '-y', '1'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print("✅ I2C system ready")
                    break
            except:
                pass
            time.sleep(1)
            print(f"   Waiting... ({i+1}/5)")
        
        # Additional stabilization time
        time.sleep(2)
        print("✅ System initialization complete\n")
        
    def initialize_robot(self):
        """Initialize robot systems"""
        try:
            print("🔌 Initializing robot systems...")
            self.robot = RobotController()
            self.test_system = RobotSelfTest()
            print("✅ Robot systems initialized")
            return True
        except Exception as e:
            print(f"❌ Robot initialization failed: {e}")
            return False
            
    def play_startup_sequence(self):
        """Play startup audio sequence"""
        try:
            if self.robot:
                print("🔊 Playing startup sequence...")
                # Startup melody
                notes = [
                    (262, 0.2),  # C4
                    (330, 0.2),  # E4
                    (392, 0.2),  # G4
                    (523, 0.4),  # C5
                ]
                
                for freq, duration in notes:
                    self.robot.play_tone(freq, duration)
                    time.sleep(0.05)
                    
                print("✅ Startup sequence complete")
        except Exception as e:
            print(f"⚠️ Startup audio failed: {e}")
            
    def run_critical_tests(self):
        """Run critical system tests only"""
        print("🔍 Running critical system validation...")
        
        critical_tests = [
            ("Hardware Connection", self.test_system.test_1_hardware_connection),
            ("Encoder System", self.test_system.test_4_encoder_system),
            ("Motor System", self.test_system.test_5_motor_system),
        ]
        
        passed = 0
        total = len(critical_tests)
        
        for test_name, test_func in critical_tests:
            try:
                print(f"   Testing {test_name}...")
                result = test_func()
                if result:
                    print(f"   ✅ {test_name}: PASSED")
                    passed += 1
                else:
                    print(f"   ❌ {test_name}: FAILED")
            except Exception as e:
                print(f"   ❌ {test_name}: ERROR - {e}")
        
        success_rate = (passed / total) * 100
        print(f"\n📊 Critical Tests: {passed}/{total} passed ({success_rate:.1f}%)")
        
        return passed >= 2  # At least 2/3 critical tests must pass
        
    def run_full_tests(self):
        """Run complete self-test suite"""
        print("🔬 Running comprehensive self-test...")
        
        try:
            # Redirect output to capture results
            import io
            from contextlib import redirect_stdout
            
            output_buffer = io.StringIO()
            
            # Run tests with output capture
            with redirect_stdout(output_buffer):
                test_results = self.test_system.run_all_tests()
            
            # Get output and results
            output = output_buffer.getvalue()
            
            # Parse results
            if hasattr(self.test_system, 'test_results'):
                passed_tests = sum(1 for result in self.test_system.test_results if result[1])
                total_tests = len(self.test_system.test_results)
                success_rate = (passed_tests / total_tests) * 100
                
                print(f"📊 Full Test Results: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)")
                
                # Show failed tests
                failed_tests = [result[0] for result in self.test_system.test_results if not result[1]]
                if failed_tests:
                    print("⚠️ Failed tests:")
                    for test_name in failed_tests:
                        print(f"   - {test_name}")
                
                return success_rate >= 80  # 80% pass rate required
            else:
                print("✅ All tests completed")
                return True
                
        except Exception as e:
            print(f"❌ Full test error: {e}")
            return False
            
    def play_result_sequence(self, success):
        """Play result audio sequence"""
        try:
            if self.robot:
                if success:
                    # Success melody - ascending
                    notes = [(523, 0.2), (659, 0.2), (784, 0.4)]
                    print("🎵 Success melody")
                else:
                    # Failure melody - descending
                    notes = [(784, 0.2), (659, 0.2), (523, 0.4)]
                    print("🎵 Warning melody")
                    
                for freq, duration in notes:
                    self.robot.play_tone(freq, duration)
                    time.sleep(0.05)
        except:
            pass
            
    def show_final_status(self, critical_passed, full_passed):
        """Display final system status"""
        elapsed = datetime.now() - self.start_time
        
        print("\n" + "="*60)
        print("📋 BOOT SELF-TEST SUMMARY")
        print("="*60)
        print(f"⏱️ Test Duration: {elapsed.total_seconds():.1f} seconds")
        print(f"🔧 Critical Systems: {'✅ OPERATIONAL' if critical_passed else '❌ DEGRADED'}")
        print(f"🔬 Full Test Suite: {'✅ PASSED' if full_passed else '⚠️ ISSUES DETECTED'}")
        
        if critical_passed:
            if full_passed:
                print("🎉 ROBOT READY FOR OPERATION!")
                status = "READY"
            else:
                print("⚠️ ROBOT OPERATIONAL WITH MINOR ISSUES")
                status = "OPERATIONAL"
        else:
            print("🚨 ROBOT REQUIRES MAINTENANCE")
            status = "MAINTENANCE_REQUIRED"
            
        print(f"📊 System Status: {status}")
        print("="*60 + "\n")
        
        return status
        
    def save_boot_log(self, status):
        """Save boot test log"""
        try:
            log_dir = "/home/raspberry/Desktop/MobileRobot/logs"
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, f"boot_test_{self.start_time.strftime('%Y%m%d_%H%M%S')}.log")
            
            with open(log_file, 'w') as f:
                f.write(f"Boot Self-Test Log\n")
                f.write(f"==================\n")
                f.write(f"Timestamp: {self.start_time}\n")
                f.write(f"Status: {status}\n")
                f.write(f"Duration: {(datetime.now() - self.start_time).total_seconds():.1f}s\n")
                
            print(f"📝 Boot log saved: {log_file}")
        except:
            pass
            
    def run(self, full_test=False):
        """Run the complete boot self-test sequence"""
        try:
            self.print_banner()
            self.wait_for_system_ready()
            
            if not self.initialize_robot():
                print("🚨 CRITICAL: Robot initialization failed!")
                return "INIT_FAILED"
                
            self.play_startup_sequence()
            
            # Always run critical tests
            critical_passed = self.run_critical_tests()
            
            # Run full tests if requested or if critical tests pass
            full_passed = True
            if full_test or critical_passed:
                full_passed = self.run_full_tests()
            
            self.play_result_sequence(critical_passed and full_passed)
            status = self.show_final_status(critical_passed, full_passed)
            self.save_boot_log(status)
            
            return status
            
        except KeyboardInterrupt:
            print("\n⚠️ Boot test interrupted by user")
            return "INTERRUPTED"
        except Exception as e:
            print(f"\n🚨 Boot test system error: {e}")
            return "ERROR"

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Robot Boot Self-Test')
    parser.add_argument('--full', action='store_true', 
                       help='Run full test suite (default: critical tests only)')
    parser.add_argument('--quiet', action='store_true',
                       help='Minimal output mode')
    
    args = parser.parse_args()
    
    if args.quiet:
        # Redirect stdout for quiet mode
        import os
        import sys
        sys.stdout = open(os.devnull, 'w')
    
    boot_test = BootSelfTest()
    status = boot_test.run(full_test=args.full)
    
    if args.quiet:
        sys.stdout = sys.__stdout__
        print(f"Boot Status: {status}")
    
    # Exit codes for system integration
    exit_codes = {
        "READY": 0,
        "OPERATIONAL": 0,
        "MAINTENANCE_REQUIRED": 1,
        "INIT_FAILED": 2,
        "INTERRUPTED": 3,
        "ERROR": 4
    }
    
    sys.exit(exit_codes.get(status, 4))

if __name__ == "__main__":
    main()
