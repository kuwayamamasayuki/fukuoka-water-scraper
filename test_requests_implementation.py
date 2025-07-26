#!/usr/bin/env python3
"""Test script for fukuoka_water_downloader.py"""

from fukuoka_water_downloader_requests import FukuokaWaterDownloader

def test_date_conversion():
    """Test date conversion functionality"""
    downloader = FukuokaWaterDownloader()
    
    print("Testing date conversion:")
    
    test_cases = [
        "令和5年1月1日",
        "平成31年4月30日", 
        "2023-01-01",
        "2023年1月1日"
    ]
    
    for date_str in test_cases:
        try:
            converted = downloader.convert_japanese_date(date_str)
            print(f"  {date_str} -> {converted}")
        except Exception as e:
            print(f"  {date_str} -> ERROR: {e}")

def test_default_date_range():
    """Test default date range generation"""
    downloader = FukuokaWaterDownloader()
    date_from, date_to = downloader.get_default_date_range()
    print(f"\nDefault date range: {date_from} to {date_to}")

if __name__ == "__main__":
    test_date_conversion()
    test_default_date_range()
    print("\nTest completed successfully!")
