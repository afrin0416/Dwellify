# 🏠 House Rent Site - Backend API


A comprehensive **Django REST Framework** backend API for a House Rent platform where users can create, browse, and manage house rental advertisements. Built with **JWT Authentication** and email verification.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2-green.svg)
![DRF](https://img.shields.io/badge/DRF-3.14-red.svg)
![JWT](https://img.shields.io/badge/Auth-JWT-orange.svg)


---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation & Setup](#-installation--setup)
- [Environment Variables](#-environment-variables)
- [API Endpoints](#-api-endpoints)
- [Authentication Guide](#-authentication-guide)
- [API Usage Examples](#-api-usage-examples)
- [Admin Setup](#-admin-setup)
- [Filtering & Search](#-filtering--search)

---

## ✨ Features

### 1. 🔐 User Authentication
- User registration with email verification 
- JWT (JSON Web Token) based authentication
- Access token & Refresh token support
- Login, Logout, Logout from all devices
- Email verification with activation link
- Resend verification email
- User profile management (view, update)
- Password change with new token generation
- Role-based access control (`admin`, `user`)

### 2. 📢 Rent Advertisements
- Users can create house rent advertisements
- Advertisements require **admin approval** before publishing
- Admin can approve or reject advertisement requests
- Only approved advertisements are visible to public
- Advertisement owner can update/delete their own ads
- Support for multiple property details (bedrooms, bathrooms, area, etc.)

### 3. 📨 Rent Requests
- Users can send rent requests to advertisement owners
- Advertisement owner can accept or reject rent requests
- When a request is **accepted**:
  - The property is marked as **rented**
- Users cannot send rent requests to their own advertisements


### 4. 🔍 Filtering & Search
- Filter advertisements by:
  - Category (ID or name)
  - City
  - Rent amount range (min/max)
  - Number of bedrooms/bathrooms
  - Rental status (available/rented)
- Ordering by rent amount, date, bedrooms

### 5. ❤️ Saving Favorites
- Users can save/bookmark favorite advertisements
- View list of all favorited advertisements
- Remove advertisements from favorites


### 6. ⭐ Reviews & Ratings
- Users can rate advertisements (1-5 stars)
- Users can add comments with ratings

### 7. 📊 Admin Dashboard
- View all pending advertisement requests
- Approve or reject advertisements
- View all advertisements with filters
- Delete any advertisement
- Dashboard statistics:
  - Total advertisements, approved, pending, rejected
  - Total rented properties
  - Total users

---

## 🛠 Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.10+** | Programming Language |
| **Django 4.2** | Web Framework |
| **Django REST Framework 3.14** | REST API |
| **SimpleJWT 5.3** | JWT Authentication |
| **django-filter 23.3** | Filtering |
| **Pillow 10.1** | Image Processing |
| **python-decouple 3.8** | Environment |



