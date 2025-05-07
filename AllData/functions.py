from rapidfuzz import fuzz, process

# Define categories with keywords
categories = {
    "Web Development": [
        "web portal", "frontend layout", "html5", "cross-browser", "static site", "semantic markup",
        "html", "css", "javascript", "react", "vue", "angular", "bootstrap",
        "frontend", "backend", "fullstack", "web app", "website", "wordpress",
        "php", "laravel", "django", "flask", "node.js", "express", "ui/ux", "responsive design"
    ],
    "Mobile Development": [
        "apk", "ipa", "mobile sdk", "native performance", "gesture support", "accelerometer", "flutter widgets",
        "mobile app development", "ios app", "android app", "mobile application",
        "android", "ios", "flutter", "react native", "swift", "kotlin", "xamarin",
        "mobile app", "mobile developer", "play store", "app store", "cross-platform", "native mobile"
    ],
    "Cyber Security": [
        "penetration test", "malware analysis", "zero day", "phishing defense", "ransomware", "network vulnerability",
        "penetration testing", "vulnerability", "soc", "firewall", "ids", "ips",
        "security audit", "ethical hacking", "forensics", "malware", "owasp",
        "cybersecurity", "network security", "siem", "zero trust"
    ],
    "Data Science": [
        "feature engineering", "data wrangling", "outlier detection", "exploratory data", "data storytelling",
        "data analysis", "data scientist", "pandas", "numpy", "eda",
        "statistics", "jupyter", "regression", "classification",
        "data visualization", "insights", "modeling", "hypothesis testing"
    ],
    "Artificial Intelligence / Machine Learning": [
        "model tuning", "training set", "overfitting", "autoencoder", "decision boundary", "transfer learning",
        "machine learning", "deep learning", "ai", "nlp", "computer vision",
        "tensorflow", "pytorch", "scikit-learn", "opencv", "transformers",
        "predictive modeling", "training models", "ai engineer"
    ],
    "Software Engineering": [
        "object-oriented", "design pattern", "versioning", "refactor", "software lifecycle", "uml",
        "c++", "java", "c#", ".net", "software developer", "oop",
        "design patterns", "architecture", "unit testing", "sdlc",
        "agile", "scrum", "version control", "git", "ide"
    ],
    "Database Management": [
        "sharding", "replication", "data warehouse", "table joins", "data schema", "rdbms",
        "sql", "mysql", "postgresql", "mongodb", "database admin",
        "data warehouse", "etl", "schemas", "nosql", "rdbms",
        "stored procedure", "query optimization", "database design", "data integrity"
    ],
    "Cloud Computing": [
        "cloud-native", "resource autoscaling", "multi-cloud", "iam roles", "serverless function",
        "aws", "azure", "google cloud", "cloud engineer", "serverless",
        "ec2", "s3", "lambda", "firebase", "cloud storage",
        "cloud architecture", "cloud-native", "infrastructure as code"
    ],
    "Networking": [
        "tcp/ip stack", "subnetting", "routing table", "dns config", "network topology", "firewall rule",
        "ccna", "network engineer", "routing", "switching", "tcp/ip",
        "lan", "wan", "vpn", "network protocols", "cisco",
        "network monitoring", "voip", "nat", "subnetting"
    ],
    "DevOps": [
        "ci/cd pipeline", "artifact repo", "container orchestration", "infrastructure code", "k8s cluster",
        "ci/cd", "jenkins", "docker", "kubernetes", "ansible", "terraform",
        "automation", "infrastructure", "gitops", "sre", "build pipeline",
        "monitoring", "deployment", "containerization"
    ],
    "Game Development": [
        "unity", "unreal engine", "game design", "gameplay", "level design",
        "multiplayer game", "2d game", "3d game", "game engine", "mobile game"
    ],
    "Embedded Systems / IoT": [
        "embedded", "firmware", "microcontroller", "arduino", "raspberry pi",
        "iot", "sensor", "real-time system", "esp32", "mcu", "hardware interface"
    ],
    "Robotics": [
        "robot", "ros", "path planning", "autonomous", "servo", "lidar",
        "actuator", "mechatronics", "robotics engineer", "motion planning"
    ],
    "Blockchain / Web3": [
        "blockchain", "web3", "solidity", "nft", "ethereum", "smart contract",
        "decentralized", "dapp", "metamask", "crypto", "token"
    ],
    "AR / VR Development": [
        "augmented reality", "virtual reality", "arcore", "arkit", "oculus",
        "mixed reality", "xr", "hololens", "360 video", "vr game"
    ],
    "Automation / Scripting": [
        "scripting", "automation", "web scraping", "selenium", "bot", "macro",
        "task automation", "process automation", "workflow automation", "headless browser"
    ],
    "ERP / CRM Systems": [
        "sap", "oracle erp", "odoo", "salesforce", "zoho", "crm system",
        "enterprise resource planning", "crm integration", "erp consultant", "business workflow"
    ],
    "Business Intelligence / Analytics": [
        "power bi", "tableau", "dashboards", "kpi", "lookml", "data studio",
        "data visualization tool", "business insights", "report builder", "bi analyst"
    ],
    "Technical Writing / Documentation": [
        "technical writing", "api documentation", "developer guide", "manual writing",
        "whitepaper", "specifications", "sdk documentation", "end-user guide"
    ],
    "E-commerce Development": [
        "shopify", "woocommerce", "magento", "bigcommerce", "ecommerce site",
        "payment gateway", "checkout system", "online store", "product catalog"
    ],
    "UI/UX and Graphic Design": [
        "figma", "adobe xd", "wireframe", "prototyping", "sketch app",
        "visual design", "graphic design", "branding", "design system", "mockup"
    ],
    "API Development / Integration": [
        "rest api", "graphql", "api integration", "third-party api",
        "api gateway", "soap", "webhooks", "openapi", "postman collection"
    ],
    "Testing / QA": [
        "qa", "unit testing", "integration testing", "test automation", "cypress",
        "test case", "selenium webdriver", "junit", "load testing", "bug tracking"
    ],
    "Educational Technology / LMS": [
        "moodle", "lms", "e-learning", "course platform", "edtech", "scorm",
        "learning management", "online training", "educational platform"
    ],
    "Audio / Speech Processing": [
        "speech recognition", "voice command", "audio signal", "asr", "speech synthesis",
        "audio classification", "voice assistant", "microphone input", "sound detection"
    ],
    "Digital Signal Processing (DSP)": [
        "fft", "digital signal", "signal processing", "filter design",
        "frequency analysis", "modulation", "dsp algorithm", "noise reduction"
    ],
    "Scientific Computing / Simulation": [
        "matlab", "simulink", "comsol", "simulation", "numerical method",
        "finite element", "monte carlo", "modeling and simulation", "scientific computing"
    ],
    "Geospatial / GIS Development": [
        "gis", "qgis", "arcgis", "geolocation", "geospatial",
        "mapbox", "leaflet", "spatial analysis", "shapefile", "cartography"
    ],
    "Computer Vision": [
        "opencv", "image processing", "object detection", "face recognition",
        "image segmentation", "computer vision", "pose estimation", "image classification"
    ],
    "Bioinformatics / Computational Biology": [
        "genomics", "bioinformatics", "sequence alignment", "protein folding",
        "genetic data", "rna", "blast", "computational biology", "biomedical data"
    ],
    "Augmented Data Annotation / Labeling": [
        "data labeling", "bounding box", "image tagging", "dataset annotation",
        "video labeling", "annotation tool", "manual tagging", "label studio"
    ],
    "Quantum Computing": [
        "quantum computing", "qiskit", "quantum circuit", "qubit",
        "quantum algorithm", "quantum entanglement", "ibmq", "quantum gate"
    ],
    "Accessibility / A11Y Engineering": [
        "accessibility", "a11y", "aria", "screen reader",
        "wcag", "keyboard navigation", "accessible ui", "color contrast"
    ],
    "Low-Code / No-Code Development": [
        "bubble.io", "webflow", "n8n", "power apps",
        "zapier", "low-code", "no-code", "workflow builder", "appgyver"
    ],
    "Search / Information Retrieval": [
        "elasticsearch", "solr", "search engine", "ranking algorithm",
        "query parser", "document indexing", "inverted index", "retrieval system"
    ],
    "Custom Hardware / FPGA Programming": [
        "fpga", "verilog", "vhdl", "hardware design",
        "synthesis", "rtl", "logic gate", "zync", "altera", "xilinx"
    ],
    "Digital Marketing Tech / Analytics": [
        "utm tracking", "google tag manager", "marketing funnel",
        "heatmap", "conversion tracking", "event tracking", "gtm", "pixels"
    ],
    "Voice Interfaces / IVR Systems": [
        "ivr", "voice bot", "twilio voice", "interactive voice",
        "voiceflow", "voice assistant", "dtmf", "call routing"
    ],
    "Marketplace / Booking Platform Development": [
        "booking system", "appointment scheduling", "multi-vendor",
        "marketplace platform", "reservation engine", "availability calendar"
    ],
    "Other / Miscellaneous": [
        "tech support", "system integration", "admin panel", "scripting task", "legacy system", "plugin customization"
    ]
}

def classify_job(desc):
    desc = desc.lower()
    best_score = 0
    best_category = None

    for category, keywords in categories.items():
        for keyword in keywords:
            score = fuzz.partial_ratio(keyword, desc)
            if score > best_score:
                best_score = score
                best_category = category

    if best_score > 0:  # Adjust this threshold if needed
        return best_category
    else:
        # Try to extract a custom but meaningful category name from first 2 words
        return "Custom Category - " + " ".join(desc.split()[:2]).capitalize()
