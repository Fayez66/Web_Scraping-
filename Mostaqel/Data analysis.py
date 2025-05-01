import re
import pandas as pd
import datetime

# Load the data
df = pd.read_csv("job_listings.csv")


# Arabic label mapping
arabic_labels = {
    "Web Development": "تطوير الويب",
    "Mobile Development": "تطوير التطبيقات",
    "Cyber Security": "الأمن السيبراني",
    "Data Science": "علم البيانات",
    "Artificial Intelligence / Machine Learning": "الذكاء الاصطناعي / تعلم الآلة",
    "Software Engineering": "هندسة البرمجيات",
    "Database Management": "إدارة قواعد البيانات",
    "Cloud Computing": "الحوسبة السحابية",
    "Networking": "الشبكات",
    "DevOps": "ديف أوبس",
    "Game Development": "تطوير الألعاب",
    "ERP system": "تخطيط موارد المؤسسات",
    "IT Support": "دعم تكنولوجيا المعلومات",
    "system testing": "اختبار النظام",
    "Other": "أخرى"
}

arabic_tags = {
"اختبار الاختراق": "Penetration Testing",
"اختبار البرمجيات": "Software Testing",
"اختبار المواقع": "Website Testing",
"اختبار تطبيقات الجوال": "Mobile App Testing",
"اختبار قابلية الاستخدام": "Usability Testing",
"استخراج البيانات": "Data Extraction",
"استشارات الشركات الناشئة": "Startup Consulting",
"استشارات قانونية": "Legal Consulting",
"استضافة المواقع": "Web Hosting",
"استكشاف الأخطاء وإصلاحها": "Troubleshooting",
"الإدارة المالية": "Financial Management",
"الإعلان": "Advertising",
"الإنتاج الصوتي": "Audio Production",
"الأمن السيبراني": "Cyber Security",
"البحث على الإنترنت": "Internet Research",
"البحث والتطوير": "Research and Development",
"البرمجة الخطية": "Linear Programming",
"البرمجة بطريقة MVC": "MVC Programming",
"التحليل الإحصائي": "Statistical Analysis",
"التحليل المالي": "Financial Analysis",
"التدقيق اللغوي": "Proofreading",
"الترجمة": "Translation",
"التسويق الإلكتروني": "Digital Marketing",
"التسويق عبر الإنترنت": "Online Marketing",
"التسويق عبر البريد الإلكتروني": "Email Marketing",
"التسويق عبر لينكد إن": "LinkedIn Marketing",
"التسويق عبر محركات البحث": "Search Engine Marketing",
"التسويق عبر مواقع التواصل الاجتماعي": "Social Media Marketing",
"التشفير": "Encryption",
"التصميم الإبداعي": "Creative Design",
"التصميم التعليمي": "Instructional Design",
"التصميم المتجاوب": "Responsive Design",
"التطوير العقاري": "Real Estate Development",
"التعلم الآلي": "Machine Learning",
"التعلم العميق": "Deep Learning",
"التعليم الإلكتروني": "E-learning",
"التقييم المالي": "Financial Evaluation",
"الحوسبة السحابية": "Cloud Computing",
"الخوارزميات": "Algorithms",
"الدعم الفني": "Technical Support",
"الذكاء الاصطناعي": "Artificial Intelligence",
"الروبوتات": "Robotics",
"الشبكات اللاسلكية": "Wireless Networks",
"العصف الذهني": "Brainstorming",
"الفكرة التصميمية": "Concept Design",
"القوائم المالية": "Financial Statements",
"الكتابة الإبداعية": "Creative Writing",
"الكتابة التقنية": "Technical Writing",
"الكتابة على الإنترنت": "Online Writing",
"اللغة الإنجليزية": "English Language",
"اللغة العربية": "Arabic Language",
"النظام الإحصائي SPSS": "SPSS Statistics",
"الهندسة": "Engineering",
"الهندسة الكهربائية": "Electrical Engineering",
"الهندسة الميكانيكية": "Mechanical Engineering",
"إدارة الاتصالات": "Communication Management",
"إدارة البريد الإلكتروني": "Email Management",
"إدارة التسويق": "Marketing Management",
"إدارة التوظيف": "Recruitment Management",
"إدارة الشبكات": "Network Management",
"إدارة المتاجر الإلكترونية": "E-commerce Management",
"إدارة المشاريع": "Project Management",
"إدارة المنتجات": "Product Management",
"إدارة المواقع": "Website Management",
"إدارة حسابات التواصل الاجتماعي": "Social Media Account Management",
"إدارة علاقات العملاء": "Customer Relationship Management",
"إدارة قواعد البيانات": "Database Management",
"إدخال بيانات": "Data Entry",
"إطار سلكي": "Wireframe",
"إظهار معماري": "Architectural Visualization",
"إعادة صياغة المحتوى": "Content Rewriting",
"إعلانات جوجل": "Google Ads",
"إليمنتور": "Elementor",
"إنتاج الفيديو": "Video Production",
"إنشاء تطبيق": "App Development",
"إنشاء حملة إعلانية": "Campaign Creation",
"إنشاء سيرة ذاتية": "CV Writing",
"إنشاء صفحة هبوط": "Landing Page Creation",
"إنشاء فيديو يوتيوب": "YouTube Video Creation",
"إنشاء متجر إلكتروني": "E-commerce Store Creation",
"إنشاء مدونة": "Blog Creation",
"إنشاء مدونة ووردبريس": "WordPress Blog Creation",
"إنشاء موقع إلكتروني": "Website Creation",
"إنشاء موقع ووردبريس": "WordPress Website Creation",
"أتمتة الاختبار": "Test Automation",
"أدوات مشرفي المواقع": "Webmaster Tools",
"أمن المعلومات": "Information Security",
"أمن وحماية المواقع": "Website Security",
"أنجولار": "Angular",
"أندرويد ستوديو": "Android Studio",
"أنظمة مدمجة": "Embedded Systems",
"أوتوكاد": "AutoCAD",
"أودو": "Odoo",
"آردوينو": "Arduino",
"باوربوينت": "PowerPoint",
"بايثون": "Python",
"بحث الكلمات المفتاحية": "Keyword Research",
"برمجة": "Programming",
"برمجة iOS": "iOS Programming",
"برمجة التطبيقات": "App Programming",
"برمجة ألعاب الجوال": "Mobile Game Programming",
"برمجة أندرويد": "Android Programming",
"برمجة تطبيقات أيفون": "iPhone Application Programming",
"برمجة تطبيقات سطح المكتب": "Desktop Application Programming",
"برمجة قواعد البيانات": "Database Programming",
"برمجة مواقع": "Website Programming",
"بناء الروابط": "Link Building",
"بناء العلامة التجارية": "Brand Building",
"بوتستراب": "Bootstrap",
"بوتستراب 5": "Bootstrap 5",
"تحرير المحتوى": "Content Editing",
"تحسين السيو الداخلي": "On-Premise SEO Optimization",
"تحسين محركات البحث": "Search Engine Optimization",
"تحليل الأسواق المالية": "Financial Market Analysis",
"تحليل الأعمال": "Business Analysis",
"تحليل البيانات": "Data Analysis",
"تحليل المنافسين": "Competitor Analysis",
"تحليل النظم": "Systems Analysis",
"تحويل PDF": "PDF Conversion",
"تحويل تصميم من PSD إلى HTML": "PSD to HTML Design Conversion",
"تخزين البيانات": "Data Warehousing",
"تخطيط موارد المؤسسات ERP": "ERP (Enterprise Resource Planning)",
"تدريب عن بعد": "Remote Training",
"تدريس خصوصي": "Private Tutoring",
"تدقيق SEO": "SEO Auditing",
"تدقيق حسابات": "Account Auditing",
"تركيب سكربتات": "Script Installation",
"تسويق منتجات": "Product Marketing",
"تصحيح برمجي": "Software Debugging",
"تصميم": "Design",
"تصميم 2d": "2D Design",
"تصميم 3D": "3D Design",
"تصميم UI UX": "UI/UX Design",
"تصميم الحقائب التدريبية": "Training Package Design",
"تصميم إعلان": "Advertising Design",
"تصميم ألعاب": "Game Design",
"تصميم بنرات": "Banner Design",
"تصميم بوسترات": "Poster Design",
"تصميم تجربة المستخدم": "User Experience Design",
"تصميم تطبيقات": "App Design",
"تصميم تطبيقات iOS": "iOS App Design",
"تصميم تطبيقات الهواتف الذكية": "Smartphone App Design",
"تصميم جرافيك": "Graphic Design",
"تصميم داش بورد": "Dashboard Design",
"تصميم دعوات": "Invitation Design",
"تصميم شعار": "Logo Design",
"تصميم صفحات الهبوط": "Landing Page Design",
"تصميم عروض بوربوينت": "PowerPoint Presentation Design",
"تصميم عروض تقديمية": "Presentation Design",
"تصميم فيديو": "Video Design",
"تصميم قواعد البيانات": "Database Design",
"تصميم قوالب": "Template Design",
"تصميم متجر إلكتروني": "E-commerce Design",
"تصميم مخططات معمارية": "Architectural Plan Design",
"تصميم ملصقات المنتجات": "Poster Design Products",
"تصميم موقع إلكتروني": "Website Design",
"تصميم موشن جرافيك": "Motion Graphic Design",
"تصميم نماذج إلكترونية": "Electronic Form Design",
"تصميم هندسي": "Architectural Design",
"تصميم هوية بصرية": "Visual Identity Design",
"تصميم هوية تجارية": "Corporate Identity Design",
"تصميم واجهة المستخدم": "User Interface Design",
"تصميمات سوشيال ميديا": "Social Media Designs",
"تصوير البيانات": "Data Visualization",
"تطوير الألعاب": "Game Development",
"تطوير البرمجيات": "Software Development",
"تطوير التطبيقات": "Application Development",
"تطوير المدونات": "Blog Development",
"تطوير الويب": "Web Development",
"تطوير الويب الكامل": "Full-Stack Web Development",
"تطوير قاعدة بيانات": "Database Development",
"تعديل الصور": "Image Editing",
"تعلم البرمجة": "Learn Programming",
"جافا": "Java",
"جافا سكريبت": "JavaScript",
"جوجل أدسنس": "Google AdSense",
"حساب كميات": "Quantity Calculation",
"حل المشكلات": "Problem Solving",
"حملة إعلانية": "Advertising Campaign",
"خدمات الويب": "Web Services",
"خدمة العملاء": "Customer Service",
"خدمة العملاء عبر الهاتف": "Call Center Customer Service",
"خطة تسويقية": "Marketing Plan",
"خطة عمل": "Business Plan",
"دعم مكتب المساعدة": "Help Desk Support",
"دوت نت فريموورك": ".NET Framework",
"راسبيري باي": "Raspberry Pi",
"رسم الخرائط": "Mapping",
"رسم يدوي": "Hand Drawing",
"سلة": "Basket",
"سيسكو": "Cisco",
"شوبيفاي": "Shopify",
"ضبط الحسابات": "Accounting Control",
"فايربيس": "Firebase",
"فوتوشوب": "Photoshop",
"فيجوال بيسك للتطبيقات": "Visual Basic for Apps",
"قوالب شوبيفاي": "Shopify Templates",
"كتابة البحوث": "Research Writing",
"كتابة التقارير": "Report Writing",
"كتابة المحتوى": "Content Writing",
"كتابة تجربة المستخدم": "User Experience Writing",
"كتابة محتوى تسويقي": "Marketing Content Writing",
"كتابة مقالات": "Article Writing",
"كتابة مقالات متوافقة مع السيو": "SEO-Friendly Article Writing",
"كوتلن": "Kotlin",
"لارافيل": "Laravel",
"لغة Sass": "Sass",
"مايكروسوفت إس كيو إل سيرفر": "Microsoft SQL Server",
"مايكروسوفت إكسل": "Microsoft Excel",
"مايكروسوفت أوفيس": "Microsoft Office",
"مايكروسوفت وورد": "Microsoft Word",
"مجموعة أدوات الويب من جوجل": "Google Web Suite",
"محاسبة": "Accounting",
"محاسبة الضرائب": "Tax Accounting",
"محاسبة تكاليف": "Cost Accounting",
"محاسبة مالية": "Financial Accounting",
"محسن مواقع الويب من جوجل": "Google Web Optimizer",
"مركز الاتصال": "Call Center",
"مساعد افتراضي": "Virtual Assistant",
"معالجة البيانات": "Data Processing",
"منصة زد": "Z Platform",
"مودل": "Moodle",
"مونتاج فيديو": "Video Editing",
"نظام لينكس": "Linux",
"نظم المعلومات الجغرافية": "GIS",
"هندسة البرمجيات": "Software Engineering",
"واجهة برمجة التطبيقات": "API",
"واقع افتراضي": "Virtual Reality",
"ووردبريس": "WordPress",
"ووكومرس": "WooCommerce",
"ويندوز سيرفر": "Windows Server",

}

# Create the Arabic category column
df['category_arabic'] = df['Category_English'].map(arabic_labels).fillna('غير معروف')
# Define a function to map each Arabic tag list to English
def map_arabic_tags_to_english(tag_string):
    if pd.isna(tag_string):
        return ''
    arabic_tags = [tag.strip() for tag in tag_string.split(',')]
    english_tags = [arabic_tags.get(tag, f"[Unmapped: {tag}]") for tag in arabic_tags]
    return ', '.join(english_tags)

# Reorder columns to place 'category_arabic' right after 'Category_English'
cols = list(df.columns)
idx = cols.index('Category_English')
# Remove and reinsert at desired position
cols.insert(idx + 1, cols.pop(cols.index('category_arabic')))
df = df[cols]

# Remove duplicates and add ID
df = df.drop_duplicates(subset=[
    'Title',
    'Category_English',
    'Posted',
    'Avg offer',
    'Duration',
    'Number of Offers',
    'Tags',
    'Tags_en',
    'Link'
])
# --- Utility Functions ---

def extract_numbers(text):
    """
    Extract and average numeric values from text.
    Handles ranges like '2 - 3' and avoids treating hyphens as negative signs.
    """
    if isinstance(text, (int, float)):
        return text

    # Replace dash variants with a space to split properly
    text = str(text).replace('–', '-').replace('—', '-').strip()

    # Explicitly match ranges like '2 - 3' or '2 to 3'
    range_match = re.findall(r'\d+(?:\.\d+)?', text)

    if range_match:
        nums = list(map(float, range_match))
        if len(nums) == 1:
            return nums[0]
        elif len(nums) >= 2:
            return sum(nums[:2]) / 2  # average of first two numbers

    return None

# --- Budget Cleaning ---
def process_file(df):
    df['Duration'] = df['Duration'].apply(extract_numbers)
    return df

df = process_file(df)

# --- Date Parsing ---
def parse_posted_date(text):
    today = datetime.date.today()
    if not isinstance(text, str):
        return text

    text = text.lower()

    if any(unit in text for unit in ['دقيقة', 'ساعة','ساعتين','ساعات']):
        return today
    elif 'يوم' in text:
        return today - datetime.timedelta(days=1)
    elif 'يومين' in text :
        return today - datetime.timedelta(days=2)
    elif 'يوما' in text or 'أيام' in text:
        return today - datetime.timedelta(days=extract_numbers(text))
    return text

df['Posted'] = df['Posted'].apply(parse_posted_date)

df['Avg offer'] = df['Avg offer'].str.strip('$')
df.rename(columns={'Duration': 'Duration(Days)'}, inplace=True)
df['Tags_en'] = df['Tags_en'].str.replace(r'[\u0600-\u06FF]', '', regex=True).str.strip()

# --- Save to CSV ---
df.to_csv("job_listings_cleaned.csv", index=False, encoding="utf-8-sig")

# Split both columns only if not null
df['Tags'] = df['Tags'].apply(lambda x: x.split(',') if isinstance(x, str) else x)
df['Tags_en'] = df['Tags_en'].apply(lambda x: x.split(',') if isinstance(x, str) else x)

# Strip whitespace in both columns
df['Tags'] = df['Tags'].apply(lambda x: [tag.strip() for tag in x] if isinstance(x, list) else x)
df['Tags_en'] = df['Tags_en'].apply(lambda x: [skill.strip() for skill in x] if isinstance(x, list) else x)

# Ensure both columns have the same number of elements per row
df = df[df['Tags'].str.len() == df['Tags_en'].str.len()]

# Convert both columns to Series and explode together
df = df.explode(['Tags', 'Tags_en']).reset_index(drop=True)

# Save to new file
df.to_csv("jobs_expanded.csv", index=False, encoding="utf-8-sig")
