# 🎨 Artiv – Real-Time Art Auction & Exhibition Platform

**Artiv** is a **real-time art auction and exhibition platform** built using **Django** and modern web technologies.
It allows **artists**, **buyers**, and **art enthusiasts** to participate in **live auctions**, explore **3D/AR/VR galleries**, and get **intelligent artwork recommendations** — blending technology with the art world.

---

## 📌 Table of Contents

1. [Project Overview](#-project-overview)
2. [Features](#-features)
3. [Tech Stack](#-tech-stack)
4. [How It Works](#-how-it-works)
5. [Screenshots](#-screenshots)
6. [Live Demo](#-live-demo)
7. [Setup Instructions](#-setup-instructions)
8. [Future Enhancements](#-future-enhancements)
9. [Contact](#-contact)

---

## 🌍 Project Overview

In the art world, accessibility and engagement are often limited to physical spaces. **Artiv** brings art auctions and exhibitions online with:

- **Real-time bidding** and notifications
- Immersive **3D/AR/VR gallery experiences**
- Intelligent recommendations using **NLP and image analysis**
- Secure payments and automated auction management
- Cloud-based deployment using **AWS services**

This project showcases how **technology and cloud computing can revolutionize art commerce and exhibitions**.

---

## ✨ Features

✅ Real-time bidding & instant notifications via **AJAX**  
✅ Immersive **AR/VR art galleries** using **WebXR**, **Three.js**, and **AR.js**  
✅ 360° artwork view using **Meshy AI** and `<model-viewer>`  
✅ NLP-based artwork sentiment analysis & recommendations (**spaCy**, **TextBlob**)  
✅ Duplicate artwork detection using **ImageHash**  
✅ Secure payments with **Razorpay** integration  
✅ Automated email notifications using **Amazon SES**  
✅ Google Sign-In using **Amazon Cognito**  
✅ Responsive, mobile-friendly design with **TailwindCSS** & **Bootstrap**  
✅ Cloud-based deployment using **Amazon Lightsail, S3 & CloudFront**  
✅ SSL/TLS security using **AWS Certificate Manager (ACM)**  

---

## 🛠️ Technologies & Services Used

- **Frontend:** HTML, CSS, JavaScript, jQuery, TailwindCSS, Bootstrap
- **Backend:** Python (Django)
- **Database:** PostgreSQL
- **Hosting:** Amazon Lightsail
- **Storage:** Amazon S3
- **CDN:** Amazon CloudFront
- **Authentication:** Amazon Cognito + Google OAuth
- **SSL/TLS:** AWS Certificate Manager (ACM)
- **Email:** Amazon SES
- **Monitoring:** Amazon CloudWatch
- **Real-Time Bidding:** AJAX
- **AR/VR Support:** WebXR, Three.js, AR.js
- **360° Art View:** Meshy AI, `<model-viewer>`
- **NLP Libraries:** spaCy, TextBlob
- **Image Processing:** ImageHash
- **Payments:** Razorpay
- **Automation:** Cron jobs

---

## ⚙ Tech Stack

**Frontend:** HTML, CSS, JavaScript, jQuery, TailwindCSS, Bootstrap  
**Backend:** Django (Python)  
**Database:** PostgreSQL  
**Cloud:** AWS Lightsail, S3, CloudFront, Cognito, SES, ACM, CloudWatch  
**3D/AR/VR:** WebXR, Three.js, AR.js, Meshy AI  
**NLP:** spaCy, TextBlob  
**Image Analysis:** ImageHash  
**Payments:** Razorpay  
**Automation:** Cron jobs  

---

## 🔄 How It Works

1. **User registers/logs in** using Django authentication or Google Sign-In through Amazon Cognito
2. **Auctions go live** with real-time bidding via AJAX
3. **Bidders receive instant updates** about auction status
4. **Winners are notified automatically** via Amazon SES
5. Users can **explore artworks in 360°/AR/VR** and get AI-powered recommendations
6. Payments are processed securely via **Razorpay**
7. The application is hosted on **Amazon Lightsail**, while static/media files are stored in **Amazon S3** and delivered through **CloudFront**

---

## 📸 Screenshots

| Auction Page | AR/VR Gallery View | 360° Artwork View |
|--------------|-------------------|-------------------|
| ![Auction Screenshot](./src/assets/auction.png) | ![Gallery Screenshot](./src/assets/gallery.png) | ![360 View Screenshot](./src/assets/360view.png) |

---

## 🎥 Live Demo

[▶ Visit Artiv – Art Auction](https://www.artiv.co.in/)

---

## 🚀 Setup Instructions

```bash
# Clone the repository
git clone https://github.com/rohitbhupat/artiv.git

# Navigate into project directory
cd artiv

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Create a superuser (admin)
python manage.py createsuperuser

# Run the development server
python manage.py runserver