# -*- coding: utf-8 -*-
import sys
import os
import time
import re

# 设置控制台编码为UTF-8
if sys.stdout.encoding != 'utf-8':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# === Configuration ===
REPORT_FOLDER_PATH = r"D:\ToddleBot\reports"
EMAIL = "vela.gan@etonhouse.com.cn"

# Class URLs
CLASS_URLS = {
    "Y2": "https://web.toddleapp.cn/platform/252570817152493601/courses/287306751395576155/journal",
    "Y3": "https://web.toddleapp.cn/platform/252570817152493601/courses/287318083301882213/journal", 
    "Y4": "https://web.toddleapp.cn/platform/252570817152493601/courses/287315881879484768/journal",
    "Y5": "https://web.toddleapp.cn/platform/252570817152493601/courses/287316523490556257/journal",
    "Y6": "https://web.toddleapp.cn/platform/252570817152493601/courses/287317283779459426/journal"
}

# Student lists
CLASS_STUDENTS = {
    "Y2": [
        "Andrew Wang", "Bilin \"Bella\" Wang", "Chelsey Cao", "Elton Poon",
        "Ethan Shen", "Henry Chen", "Ian An", "James Zexiang Otley", 
        "Janice Lim", "Kaitlinn Pan", "Kevin Wang", "Laurence Liang", 
        "Louis Zeao Otley", "Morgan Emeka", "Rain Sun", "Riley Chen", "Rosen Luo"
    ], 
    "Y3": [
        "Aria Shi", "Eason Yuan", "Enrui Yan", "Evan Cao Pellerin", 
        "Gordon Tan", "Hailey Yuan", "Karina Pan", "Kyle Chen", 
        "Mia Hung", "Priscilla Hui", "Samrat Xiao", "Yanjin Luli"
    ],
    "Y4": [
        "Annabel Li", "Anna Cavaliere", "Anqi Liang", "Elaine Hou", 
        "Enyu Yan", "James Feng", "Jesse Chen", "Julianna Tong", "Luna Wong", 
        "Mini TZE YEE Lee", "Nina Hung", "Phoebus Li", "Polok Cheng", "Vanessa Tong",
        "Wayne Liang"
    ],  
    "Y5": [
        "Aarya Chen", "Ally Yang", "Anan Ma", "Cheryl Leung", "Chloe Cai", "Elroy Zeng",
        "Elwyn Li", "Jayden Lun", "Kety Wang", "Louis Lin", "Sophia Li", "Uyi Li"
    ], 
    "Y6": [
        "Annie Le", "Cindy Yang", "Eddie Yang", "Emilia Chen", "Enqi Yan", "Jason Feng",
        "Jayden Duan", "Larry Wang", "Melinda Guo"
    ]
}

# Description types mapping
DESCRIPTION_TYPES = {
    "SR": "Please read others' work and provide comments as required.",
    "WT": "This week's vocabulary test. Please correct errors (1 error = 5 corrections) and paste it on the back cover of your textbook for targeted review.",
    "OF": "Rewrite",
    "HW": "This is the student's homework assignment.",
    "CW": "This is the student's classwork.",
    "PR": "This is the student's project work."
}

# Share types mapping
SHARE_TYPES = {
    "SP": "Students and Families",
    "PO": "Families Only", 
    "SO": "Students Only",
    "TO": "Private"
}

# Global variable for custom description
CUSTOM_DESCRIPTION = ""

# === Chrome Options ===
chrome_options = Options()
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors")
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument("--allow-running-insecure-content")
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

# === Initialize Driver ===
print("🚀 Starting Toddle Multi-Class Auto Upload System...")
print("🔧 Auto-configuring ChromeDriver...")

try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    print("✅ ChromeDriver configured successfully!")
    
except Exception as e:
    print(f"❌ ChromeDriver configuration failed: {e}")
    print("💡 Trying backup solution...")
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("✅ Backup solution started successfully!")
    except Exception as e2:
        print(f"❌ All startup methods failed: {e2}")
        print("Please check:")
        print("1. Chrome browser is installed")
        print("2. Network connection is working")
        print("3. System permissions are sufficient")
        input("Press Enter to exit...")
        exit(1)

wait = WebDriverWait(driver, 15)

def get_description_choice():
    """Let user choose description type"""
    global CUSTOM_DESCRIPTION
    
    print("\n" + "=" * 60)
    print("📝 CHOOSE DESCRIPTION METHOD")
    print("=" * 60)
    print("1. Use default descriptions (auto-selected by file type)")
    print("2. Enter custom description (same for all files)")
    print("=" * 60)
    
    while True:
        choice = input("Please choose (1 or 2): ").strip()
        if choice == "1":
            print("✅ Selected: Use default descriptions")
            return "default"
        elif choice == "2":
            print("\n💬 Please enter custom description:")
            custom_desc = input("Description: ").strip()
            if custom_desc:
                CUSTOM_DESCRIPTION = custom_desc
                print(f"✅ Custom description set: {CUSTOM_DESCRIPTION}")
                return "custom"
            else:
                print("❌ Description cannot be empty, please re-enter")
        else:
            print("❌ Please enter 1 or 2")

def show_naming_guide():
    """Show file naming guide"""
    print("\n" + "=" * 80)
    print("📋 FILE NAMING GUIDE")
    print("=" * 80)
    print("🎯 Format: Grade-DescType-ShareType-PImageNum(StudentNum)")
    print("")
    print("📝 Field Explanation:")
    print("  📍 Grade: Y2, Y3, Y4, Y5, Y6")
    print("  📍 DescType: SR(Peer Review), WT(Vocab Test), OF(Rewrite), HW(Homework), CW(Classwork), PR(Project)")
    print("  📍 ShareType: SP(Students+Families), PO(Families Only), SO(Students Only), TO(Private)")
    print("  📍 PImageNum: P1(1st image), P2(2nd image), P3(3rd image)...")
    print("  📍 StudentNum: (1), (2), (3)... Student position in class list")
    print("")
    print("📚 Batch Naming Example:")
    print("  ✅ Y3-WT-SP-P1(1).jpg  → Select multiple files & rename →")
    print("  ✅ Y3-WT-SP-P1(2).jpg  → Auto-generate sequential numbers")
    print("  ✅ Y3-WT-SP-P1(3).jpg  → Perfect for quick batch naming")
    print("")
    print("💡 Batch Naming Tips:")
    print("  1. Select all 1st images → Rename to Y3-WT-SP-P1(1) → Auto-generate P1(1), P1(2), P1(3)...")
    print("  2. Select all 2nd images → Rename to Y3-WT-SP-P2(1) → Auto-generate P2(1), P2(2), P2(3)...")
    print("=" * 80)

def parse_filename(filename):
    """
    Parse filename to extract grade, description type, share type, image number and student number
    New format: Grade-DescType-ShareType-PImageNum(StudentNum)
    Example: Y3-WT-SP-P1(1)
    """
    name_without_ext = os.path.splitext(filename)[0]
    
    pattern = r'^(Y[2-6])-([A-Z]{2})-([A-Z]{2})-P(\d+)\((\d+)\)$'
    match = re.match(pattern, name_without_ext)
    
    if match:
        grade = match.group(1)
        desc_type = match.group(2)
        share_type = match.group(3)
        image_index = int(match.group(4))
        student_index = int(match.group(5))
        
        return {
            'grade': grade,
            'desc_type': desc_type,
            'share_type': share_type,
            'image_index': image_index,
            'student_index': student_index,
            'valid': True
        }
    else:
        print(f"⚠️ Invalid filename format: {filename}")
        print("  Correct format: Grade-DescType-ShareType-PImageNum(StudentNum)")
        print("  Example: Y3-WT-SP-P1(1).jpg")
        return {'valid': False}

def get_student_files_grouped():
    """Get and group files by student"""
    files_info = []
    
    if not os.path.exists(REPORT_FOLDER_PATH):
        print(f"❌ Reports folder not found: {REPORT_FOLDER_PATH}")
        return {}
    
    for filename in os.listdir(REPORT_FOLDER_PATH):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf')):
            file_info = parse_filename(filename)
            if file_info['valid']:
                file_info['filename'] = filename
                file_info['file_path'] = os.path.join(REPORT_FOLDER_PATH, filename)
                files_info.append(file_info)
    
    student_files = {}
    for file_info in files_info:
        key = (file_info['grade'], file_info['student_index'])
        if key not in student_files:
            student_files[key] = []
        student_files[key].append(file_info)
    
    for key in student_files:
        student_files[key].sort(key=lambda x: x['image_index'])
    
    print(f"📁 Found {len(files_info)} valid files, involving {len(student_files)} students")
    return student_files

def auto_fill_email():
    """Auto-fill email address"""
    print(f"📧 Attempting to auto-fill email: {EMAIL}...")
    try:
        time.sleep(3)
        
        email_selectors = [
            'input[type="email"]',
            'input[name="email"]',
            'input[placeholder*="email" i]',
            'input[autocomplete="email"]'
        ]
        
        for selector in email_selectors:
            try:
                email_input = driver.find_element(By.CSS_SELECTOR, selector)
                email_input.clear()
                email_input.send_keys(EMAIL)
                print(f"✅ Email auto-filled: {EMAIL}")
                return True
            except:
                continue
        
        print("⚠️ Email input not found, please fill manually")
        return False
    except Exception as e:
        print(f"⚠️ Auto-fill email failed: {e}")
        return False

def safe_find_element(selectors, by=By.CSS_SELECTOR, timeout=10):
    """Safely find element with retry"""
    for attempt in range(3):
        try:
            if by == By.CSS_SELECTOR:
                for selector in selectors:
                    try:
                        element = WebDriverWait(driver, timeout).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        return element
                    except:
                        continue
            elif by == By.XPATH:
                for selector in selectors:
                    try:
                        element = WebDriverWait(driver, timeout).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                        return element
                    except:
                        continue
        except Exception as e:
            if attempt == 2:
                print(f"  ⚠️ Element not found: {selectors}")
                return None
            time.sleep(2)
    return None

def safe_click(element):
    """Safely click element"""
    try:
        element.click()
        return True
    except Exception as e:
        print(f"  ⚠️ Click failed: {e}")
        return False

def add_work_description(desc_type, desc_choice):
    """Add work description"""
    print(f"  Step 6: Adding work description...")
    try:
        if desc_choice == "custom":
            description_text = CUSTOM_DESCRIPTION
            print(f"  📝 Using custom description")
        else:
            description_text = DESCRIPTION_TYPES.get(desc_type, "This is the student's work showcase, demonstrating progress and achievements in the learning process.")
            print(f"  📝 Using default description: {desc_type}")
        
        description_selectors = [
            '[data-test-id="createpost-description-textarea"]',
            'textarea[placeholder*="Description"]',
            'textarea[placeholder*="描述"]',
            'div[contenteditable="true"]'
        ]
        
        for selector in description_selectors:
            try:
                description_box = driver.find_element(By.CSS_SELECTOR, selector)
                description_box.clear()
                description_box.send_keys(description_text)
                print(f"  ✅ Description added")
                time.sleep(1)
                return True
            except:
                continue
        print("  ⚠️ Description box not found, skipping")
        return True
    except Exception as e:
        print(f"  ⚠️ Add description failed: {e}")
        return True

def set_sharing_option(share_type):
    """Set sharing options"""
    print(f"  Step 7: Setting sharing option - {share_type}...")
    
    if share_type == "SO":
        try:
            print("  🔧 Attempting to set 'Students Only'...")
            share_button = driver.find_element(By.XPATH, '//span[contains(text(), "共享于")]/ancestor::button')
            driver.execute_script("arguments[0].click();", share_button)
            time.sleep(2)
            
            options = driver.find_elements(By.XPATH, "//div[contains(@class, 'option')]")
            if len(options) >= 3:
                driver.execute_script("arguments[0].click();", options[2])
                print("  ✅ Selected third option (Students Only)")
            
            done_button = driver.find_element(By.XPATH, "//button[.//span[text()='已完成']]")
            driver.execute_script("arguments[0].click();", done_button)
            time.sleep(2)
            return True
        except:
            print("  ⚠️ Setting failed, using default")
            return True
    else:
        print(f"  ⏭️ Using default setting: {SHARE_TYPES.get(share_type)}")
        return True

def upload_multiple_files_for_student(file_infos, desc_choice):
    """Upload multiple files for a single student"""
    if not file_infos:
        return False
    
    first_file = file_infos[0]
    grade = first_file['grade']
    desc_type = first_file['desc_type']
    share_type = first_file['share_type']
    student_index = first_file['student_index'] - 1
    
    student_names = CLASS_STUDENTS.get(grade, [])
    if student_index >= len(student_names):
        print(f"  ❌ Student number {student_index + 1} out of range, class {grade} has only {len(student_names)} students")
        return False
    
    student_name = student_names[student_index]
    file_count = len(file_infos)
    
    print(f"\n🎯 Processing student: {student_name} (Class: {grade}, Files: {file_count})")
    for i, file_info in enumerate(file_infos):
        print(f"    📄 {i+1}. {file_info['filename']}")
    
    # 1. Click student
    print("  Step 1: Clicking student...")
    student_element = safe_find_element([f"//div[contains(text(), '{student_name}')]"], By.XPATH)
    if not student_element or not safe_click(student_element):
        print(f"  ❌ Cannot click student: {student_name}")
        return False
    print("  ✅ Student clicked successfully")
    time.sleep(3)
    
    # 2. Click create post
    print("  Step 2: Clicking create post...")
    create_button = safe_find_element(['[data-test-id="journal-feed-createpost-button"]'])
    if not create_button or not safe_click(create_button):
        print("  ❌ Cannot click create post")
        return False
    print("  ✅ Create post successful")
    time.sleep(3)
    
    # 3. Click photo button
    print("  Step 3: Clicking photo button...")
    photo_button = safe_find_element(['[data-test-id="attachmentitemtypeselection-PHOTO"]'])
    if not photo_button or not safe_click(photo_button):
        print("  ❌ Cannot click photo button")
        return False
    print("  ✅ Photo button successful")
    time.sleep(2)
    
    # 4. Click upload from device
    print("  Step 4: Clicking upload from device...")
    upload_button = safe_find_element(['[data-test-id="attachmentitemtypesubmenu-upload_photo_video_from_device:PHOTO"]'])
    if not upload_button or not safe_click(upload_button):
        print("  ❌ Cannot click upload from device")
        return False
    print("  ✅ Upload from device successful")
    time.sleep(2)
    
    # 5. Multiple file upload
    print(f"  Step 5: Uploading {file_count} files...")
    file_input = safe_find_element(["input[type='file']"])
    if not file_input:
        print("  ❌ File upload input not found")
        return False
    
    try:
        file_paths = [file_info['file_path'] for file_info in file_infos]
        file_input.send_keys("\n".join(file_paths))
        print(f"  ✅ Multiple files uploaded: {file_count} files")
        time.sleep(5)
    except Exception as e:
        print(f"  ❌ File upload failed: {e}")
        return False
    
    # 6. Add work description
    add_work_description(desc_type, desc_choice)
    
    # 7. Set sharing option
    set_sharing_option(share_type)
    
    # 8. Publish
    print("  Step 8: Publishing work...")
    for attempt in range(3):
        try:
            publish_button = safe_find_element([
                '[data-test-id="journal-postcreation-publish-button"]',
                '[data-test-id="createpost-publish-button"]'
            ], timeout=10)
            
            if not publish_button:
                print(f"  ⚠️ Attempt {attempt + 1}: Publish button not found")
                time.sleep(3)
                continue
                
            if safe_click(publish_button):
                time.sleep(5)
                
                current_url = driver.current_url
                if "journal" in current_url:
                    print("  ✅ Published successfully!")
                    print(f"🎉 {student_name}'s {file_count} files completed!")
                    try:
                        import winsound
                        winsound.Beep(1000, 300)
                    except:
                        pass
                    return True
                else:
                    print(f"  ⚠️ Attempt {attempt + 1}: Page issue after publish")
            else:
                print(f"  ⚠️ Attempt {attempt + 1}: Click publish button failed")
                
        except Exception as e:
            print(f"  ⚠️ Attempt {attempt + 1} failed: {e}")
        
        time.sleep(3)
    
    print("  ❌ Publish failed, max retries reached")
    return False

def switch_to_class(grade):
    """Switch to specified class page"""
    print(f"\n🔄 Switching to class {grade}...")
    class_url = CLASS_URLS.get(grade)
    if not class_url:
        print(f"❌ Class URL not found for {grade}")
        return False
    
    try:
        driver.get(class_url)
        time.sleep(5)
        print(f"✅ Successfully switched to class {grade}")
        return True
    except Exception as e:
        print(f"❌ Switch to class {grade} failed: {e}")
        return False

def recover_browser():
    """Recover browser state"""
    print("  🔄 Recovering browser state...")
    try:
        driver.back()
        time.sleep(3)
        print("  ✅ Browser recovered successfully")
        return True
    except Exception as e:
        print(f"  ❌ Browser recovery failed: {e}")
        return False

def main():
    """Main execution flow"""
    try:
        show_naming_guide()
        desc_choice = get_description_choice()
        student_files = get_student_files_grouped()
        
        if not student_files:
            print("❌ No files found to upload, please check filename format and folder path")
            return
        
        print("\n📋 Found files grouped by student:")
        for (grade, student_idx), files in student_files.items():
            student_names = CLASS_STUDENTS.get(grade, [])
            if student_idx <= len(student_names):
                student_name = student_names[student_idx - 1]
                print(f"  👤 {student_name} ({grade}-{student_idx}): {len(files)} files")
                for file_info in files:
                    print(f"     📄 {file_info['filename']}")
        
        login_url = "https://web.toddleapp.cn/platform/252570817152493601/courses/287317283779459426/journal?type=loginFormV3&usertype=staff"
        print(f"\n🚀 Opening login page: {login_url}")
        driver.get(login_url)
        driver.maximize_window()
        time.sleep(3)
        
        auto_fill_email()
        
        print("\n" + "=" * 60)
        print("🔐 LOGIN INSTRUCTIONS")
        print("=" * 60)
        print("1. Email auto-filled, please enter password")
        print("2. Complete login")
        print("3. Ensure you see student list")
        print("4. Return here and press Enter to start upload")
        print("=" * 60)
        
        input("👉 Press Enter after login to start upload...")
        
        print("\n🎊 Starting batch upload for all classes!")
        print(f"📊 Total students: {len(student_files)}")
        total_files = sum(len(files) for files in student_files.values())
        print(f"📊 Total files: {total_files}")
        if desc_choice == "custom":
            print(f"📝 Using custom description: {CUSTOM_DESCRIPTION}")
        else:
            print("📝 Using default type descriptions")
        print("=" * 60)
        
        start_time = time.time()
        success_count = 0
        failed_students = []
        
        files_by_grade = {}
        for (grade, student_idx), files in student_files.items():
            if grade not in files_by_grade:
                files_by_grade[grade] = []
            files_by_grade[grade].append((student_idx, files))
        
        for grade, student_data in files_by_grade.items():
            print(f"\n🏫 Processing class {grade}...")
            
            if not switch_to_class(grade):
                print(f"❌ Cannot switch to class {grade}, skipping all students")
                for student_idx, files in student_data:
                    failed_students.append((grade, student_idx, files))
                continue
            
            for i, (student_idx, files) in enumerate(student_data):
                student_names = CLASS_STUDENTS.get(grade, [])
                student_name = student_names[student_idx - 1] if student_idx <= len(student_names) else f"Student{student_idx}"
                
                print(f"\n{'='*50}")
                print(f"Progress: {i+1}/{len(student_data)} (Class: {grade})")
                print(f"Student: {student_name} ({len(files)} files)")
                print(f"{'='*50}")
                
                result = upload_multiple_files_for_student(files, desc_choice)
                
                if result:
                    success_count += 1
                    print(f"🎉 Completed: {student_name}'s {len(files)} files")
                else:
                    failed_students.append((grade, student_idx, files))
                    print(f"❌ Failed: {student_name}'s {len(files)} files")
                
                progress = (success_count + len(failed_students)) / len(student_files) * 100
                print(f"📈 Overall progress: {progress:.1f}%")
                
                if i < len(student_data) - 1:
                    if not recover_browser():
                        print("❌ Browser recovery failed, stopping")
                        break
        
        end_time = time.time()
        total_time = (end_time - start_time) / 60
        
        print(f"\n{'='*60}")
        print("🎊 Multi-class Batch Upload Completed!")
        print(f"{'='*60}")
        print(f"✅ Success: {success_count}/{len(student_files)} students")
        print(f"📊 Total files: {total_files}")
        print(f"⏱️ Total time: {total_time:.1f} minutes")
        
        if failed_students:
            print(f"❌ Failed students:")
            for grade, student_idx, files in failed_students:
                student_names = CLASS_STUDENTS.get(grade, [])
                student_name = student_names[student_idx - 1] if student_idx <= len(student_names) else f"Student{student_idx}"
                print(f"  - {student_name} ({grade}): {len(files)} files")
        else:
            print("🌟 Perfect! All students' files uploaded successfully!")
        
        print("💡 Tip: Upload process completed, you can close the browser")
        print(f"{'='*60}")
        
        try:
            import winsound
            for i in range(3):
                winsound.Beep(1000, 300)
                time.sleep(0.2)
        except:
            print("🔊 Completion sound")

    except Exception as e:
        print(f"💥 System error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("\n🛑 Program execution completed")
        input("Press Enter to close browser...")
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    main()