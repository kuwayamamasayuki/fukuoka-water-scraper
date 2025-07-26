#!/usr/bin/env python3
"""Test script for date conversion functionality"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fukuoka_water_downloader_requests import FukuokaWaterDownloader

def test_date_conversion():
    """Test date conversion functionality"""
    downloader = FukuokaWaterDownloader()
    
    print("Testing date conversion to kenYm format:")
    
    test_cases = [
        ("令和7年5月", "令和　７年　５月検針分"),
        ("令和5年1月", "令和　５年　１月検針分"),
        ("平成31年4月", "平成　３１年　４月検針分"),
        
        ("2025-05", "令和　７年　５月検針分"),
        ("2023-01", "令和　５年　１月検針分"),
        ("2019-04", "令和　１年　４月検針分"),
        ("2018-12", "平成　３０年　１２月検針分"),
        
        ("2025年5月", "令和　７年　５月検針分"),
        ("2023年1月", "令和　５年　１月検針分"),
        
        ("2025-05-15", "令和　７年　５月検針分"),
        ("2023-01-01", "令和　５年　１月検針分"),
    ]
    
    all_passed = True
    
    for input_date, expected in test_cases:
        try:
            result = downloader.convert_date_to_kenyin_format(input_date)
            status = "✓" if result == expected else "✗"
            if result != expected:
                all_passed = False
            print(f"  {status} '{input_date}' -> '{result}' (expected: '{expected}')")
        except Exception as e:
            print(f"  ✗ '{input_date}' -> ERROR: {e}")
            all_passed = False
    
    try:
        result = downloader.convert_date_to_kenyin_format("")
        print(f"  ✓ '' -> '{result}' (current date)")
    except Exception as e:
        print(f"  ✗ '' -> ERROR: {e}")
        all_passed = False
    
    return all_passed

if __name__ == "__main__":
    success = test_date_conversion()
    print(f"\nDate conversion test {'PASSED' if success else 'FAILED'}!")
    sys.exit(0 if success else 1)
