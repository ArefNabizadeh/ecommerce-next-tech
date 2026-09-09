<div align="center">

# 🛒 Next Tech — Django E-commerce Platform

A modern, Persian-first electronics e-commerce web application built with **Django**, **Tailwind CSS**, and **Alpine.js**.

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-092E20?logo=django)](https://www.djangoproject.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-4-38B2AC?logo=tailwindcss)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](#license)

**[🔗 Live Demo](https://next-tech-green.vercel.app)**

</div>

---

## 📸 Screenshots

<!--
راهنمای جایگذاری عکس در پایین توضیح داده شده — همین‌جا با همین سینتکس جایگزینش کن:
-->

![Home page](https://github.com/user-attachments/assets/4fa644e2-12a0-43af-8d7c-b0ff7181e359)

---

## 📖 Overview

**Next Tech** is a full-featured electronics storefront covering the complete customer journey — product discovery, cart, checkout, order tracking, coupons, a customer dashboard, and a companion blog — built as a Django capstone project with production-grade modeling patterns (custom user model, price snapshotting on orders, protected foreign keys on catalog data, and activity logging).

> 🇮🇷 The UI, validation messages, and locale (`fa-ir`, Asia/Tehran) are fully Persian-first.

---

## ✨ Features

- **Product catalog** — brands, categories, image galleries, dynamic key/value specifications, reviews & ratings, wishlists, flash-sale banners
- **Cart & Checkout** — per-user persistent cart, multi-step checkout, shipping method & payment method selection
- **Order management** — auto-generated order numbers (`ORD-YYYYMMDD-NNNN`), status/payment tracking, price snapshotting so historical orders never change if a product's price changes later
- **Coupons** — percentage or fixed-amount discounts, usage limits, min-order thresholds, per-user redemption tracking
- **Customer dashboard** — profile, saved addresses (with a single default address), order history, wishlist
- **Blog** — categories, tags, draft/published/archived workflow, auto-computed reading time
- **Activity log** — every meaningful user action (orders, wishlist changes, logins, profile edits) is recorded with metadata and IP address

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 6.0 (Python 3.13) |
| Database | SQLite (dev) |
| Styling | Tailwind CSS 4 (CLI build) |
| Interactivity | Alpine.js |
| Image handling | Pillow |
| Coupons | django-coupons |
| Package management | Poetry / pip |

---

## 📁 Project Structure

```
ecommerce-next-tech/
├── apps/                  # feature-modular Django apps
│   ├── core/               # home page, error pages, shared context processors
│   ├── accounts/           # custom User, Profile, Address, activity log
│   ├── products/           # Brand, Category, Product, reviews, wishlist, flash sales
│   ├── cart/                # cart & cart items
│   ├── orders/             # orders & order items, checkout logic
│   ├── dashboard/          # customer-facing account dashboard
│   ├── blog/                # articles, tags, categories
│   └── discounts/          # coupon codes
├── config/                 # settings, root urls, wsgi/asgi
├── templates/               # HTML templates, mirrored per app + shared partials/
├── static/                  # compiled Tailwind CSS, JS, fonts, images
├── manage.py
└── requirements.txt
```

---

## ⚙️ Local Setup

### 1. Clone & install Python dependencies

```bash
git clone https://github.com/ArefNabizadeh/ecommerce-next-tech.git
cd ecommerce-next-tech
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
```

> `SECRET_KEY` is read from the environment (`config/settings.py`) and the app will refuse to start without it — generate one with:
> `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

### 3. Install & build Tailwind CSS

```bash
npm install
npm run dev      # watches static/src/input.css → static/css/output.css
```

### 4. Run migrations & start the server

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit **http://127.0.0.1:8000**.

---

## 🗺️ Roadmap

- [ ] Add automated test coverage (unit + integration)
- [ ] Introduce a proper role system (Admin / Seller / Customer) instead of relying solely on `is_staff`
- [ ] Move from SQLite to a managed PostgreSQL database for production
- [ ] Connect `FlashSale` to specific products
- [ ] Add a real payment gateway integration

---

## 📄 License

This project is licensed under the MIT License.

---

<div align="center">
Built with ❤️ by <a href="https://github.com/ArefNabizadeh">Aref Nabizadeh</a>
</div>
