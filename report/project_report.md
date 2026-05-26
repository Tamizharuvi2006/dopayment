# Project Report
## DoPayments: Smart Retail-Distributor Business Management and Financial Intelligence System

**Submitted in partial fulfillment for the Final Year Project**

**Developed Using:**
* **Frontend:** HTML5, Vanilla CSS (Production Design System), Vanilla JavaScript
* **Backend:** Python (Flask), SQLAlchemy, Scikit-Learn
* **Database:** SQLite
* **Current Build Status:** UI/UX upgraded, navigation bugs fixed, frontend JavaScript syntax verified, and backend Python modules compiled successfully.

---

### 1. Abstract
The **DoPayments** project is a comprehensive and intelligent business management platform designed to unify the ecosystem of retailers, distributors, super stockists, and manufacturers. Addressing the common inefficiencies in traditional retail and distribution networks, this system provides real-time stock handling, sales tracking, credit cycle management, and advanced AI-driven demand forecasting. A unique feature of this platform is the **Money Split Concept**, an innovative financial planning tool that intelligently allocates incoming revenue into strategic buckets such as stock purchase, operations, retailer credit, and emergency reserves, thereby ensuring financial stability and sustainable business growth.

### 2. Problem Statement
Traditional retail and distribution systems often suffer from poor coordination and lack of actionable insights. Key challenges include:
* **Inventory Mismanagement:** Frequent stock shortages or overstocking due to poor demand understanding.
* **Inefficient Cash Flow:** Struggling to balance incoming revenue across multiple business needs (e.g., stock purchases vs. operational expenses).
* **Weak Credit Management:** Difficulty in tracking retailer credit cycles, leading to delayed payments and bad debt.
* **Lack of Strategic Insights:** Absence of data-driven tools for cash rotation analysis and future demand forecasting.

DoPayments aims to digitize and optimize these operations while introducing intelligent decision-making support to overcome these challenges.

### 3. Objectives
* To monitor stock levels, sales, and profitability in real time.
* To manage retailer-distributor relationships efficiently.
* To implement a structured **Money Split** concept for financial planning and discipline.
* To track and improve credit cycles and maintain healthy cash flow.
* To optimize cash rotation by identifying quick-cash retailers and fast-moving products.
* To forecast future demand using historical data and Machine Learning models.
* To improve communication and visibility across the supply chain.

### 4. System Architecture & Technology Stack
The project follows a standard Client-Server architecture with a RESTful API bridging the frontend and backend.
* **Frontend:** Built entirely with raw HTML, CSS, and Vanilla JavaScript to ensure maximum performance and complete control over the production interface. A custom design system was created using CSS variables for theme management, consistent spacing, restrained borders, professional card surfaces, responsive grids, accessible focus states, and shared mobile navigation. Chart.js is used for data visualization.
* **Backend:** Developed using Python with the Flask framework. It provides robust REST API endpoints to serve data to the frontend.
* **Database:** SQLite is used for local prototyping via SQLAlchemy ORM, designed for easy migration to PostgreSQL or MySQL for production deployment.
* **Analytics/AI:** Scikit-Learn and NumPy are used on the backend to perform Linear Regression for the Demand Forecasting module.

### 5. Core Modules Overview

#### 5.1 Retailer Management Module
Handles CRUD operations for retailers and their product catalogs. Tracks live stock-in-hand with low-stock alerts, monitors daily sales, and analyzes brand-wise profitability.

#### 5.2 Distributor Management Module
Provides a hub for distributors to view retailer relationships, map area-wise demand, track best-selling products, and manage product inquiries.

#### 5.3 Money Split Management Module (Unique Innovation)
An interactive financial planner that allocates incoming funds into five strategic categories: Stock Purchase, Retailer Credit, Operational Expenses, Emergency Reserve, and Savings. This ensures balanced growth and risk mitigation.

#### 5.4 Credit Cycle Management Module
Maintains a credit ledger for retailers. Tracks outstanding balances, credit limits, and credit health scores. Includes overdue alerts and payment recording functionality.

#### 5.5 Cash Rotation Analysis Module
Analyzes product rotation speed (days to sell) and identifies quick-cash retailers, helping businesses optimize their working capital and reinvestment strategies.

#### 5.6 Demand Forecasting Module
Utilizes a Python-based Linear Regression model to study historical sales data across different areas and age groups. It predicts the stock requirements for the upcoming three months, preventing stockouts and overstocking.

#### 5.7 Super Stockist & Market Intelligence Module
Tracks super stockist performance against targets, logs daily retailer visits, and records visit outcomes to gauge market penetration and efficiency.

#### 5.8 Communication Hub
A built-in messaging system facilitating direct communication channels between Retailers ↔ Distributors and Distributors ↔ Manufacturers.

### 6. UI/UX and Operational Improvements
The latest project update focused on making the product interface more professional, production-ready, and operationally reliable.

Key improvements include:
* **Production design system refinement:** Reduced excessive rounding, improved shadows, stabilized spacing, corrected focus states, and made tables, cards, badges, buttons, modals, and forms more consistent.
* **Responsive application shell:** Added a shared mobile navigation controller so every dashboard module can be accessed on tablet and mobile screens.
* **Professional icon system:** Replaced emoji-style interface icons with a local SVG icon renderer across the login page, dashboard, navigation, cards, buttons, alerts, forms, and dynamic toasts.
* **Original brand logo:** Replaced dummy text logo marks with the supplied Do Payment logo image across the login screen, sidebar, and dashboard modules.
* **Sample data removal:** Removed frontend hardcoded sample records, disabled automatic sample-data seeding, and cleared the local SQLite database tables so the system starts with real operational data only.
* **Improved accessibility and interaction:** Added keyboard Escape handling for open modals/navigation, visible focus states, disabled button styling, better wrapping in topbar actions, and safer mobile layouts.
* **Authentication flow correction:** Fixed the dashboard unauthenticated redirect path and removed demo login behavior so authentication depends on backend users.
* **Dashboard and chart fixes:** Updated dashboard chart styling to match the light professional theme and fixed the Demand Forecast chart so all top product series show their predicted months.
* **Money Split bug fix:** Corrected amount formatting in allocation results to avoid duplicate currency symbols on smaller values.

### 7. Database Schema Design
The system utilizes a relational database structure with the following core entities:
* **Users:** Authentication and role management (Admin, Retailer, Distributor, Super Stockist).
* **Retailers & Products:** Core inventory and client management.
* **Sales:** Transactional records linked to Retailers and Products.
* **Credits:** Ledger entries tracking borrowed amounts, due dates, and statuses.
* **MoneySplits:** Historical records of revenue allocations.
* **Super Stockists & Visits:** Tracking field staff performance and activity logs.
* **DemandRecords & Messages:** Historical data for AI forecasting and communication logs.

### 8. Expected Outcomes and Impact
* **Financial Stability:** The Money Split concept guarantees that operational costs and savings are always accounted for, reducing the risk of bankruptcy.
* **Optimized Inventory:** AI-driven forecasting ensures capital is not tied up in dead stock while preventing missed sales due to stockouts.
* **Improved Relationships:** Transparent credit tracking and communication hubs build trust between supply chain partners.
* **Data-Driven Decisions:** Comprehensive dashboards provide instant visibility into business health, replacing guesswork with analytics.

### 9. Testing and Verification
The following verification was completed after the UI/UX and bug-fix pass:
* **Backend syntax verification:** `python -m compileall backend` completed successfully.
* **Targeted backend module verification:** `python -m py_compile backend\app.py backend\routes\auth.py backend\routes\forecast.py` completed successfully.
* **Frontend JavaScript syntax verification:** All inline scripts, `assets/js/app-shell.js`, and `assets/js/pro-icons.js` passed JavaScript syntax checks.
* **Static asset smoke test:** `index.html`, `dashboard.html`, `assets/css/global.css`, `assets/js/app-shell.js`, and `assets/js/pro-icons.js` served successfully from a local static server.

Note: Long-running background servers could not be kept alive inside the current sandbox session, so visual browser QA was limited to static asset and script verification.

### 10. Future Scope
While the current prototype is fully functional, future enhancements could include:
* Integration with real banking APIs and Payment Gateways for automated fund splitting.
* Implementation of more advanced Deep Learning models (e.g., LSTM) for time-series demand forecasting considering seasonality.
* Development of native mobile applications (using Flutter or React Native) for field super stockists.
* Cloud deployment using AWS or Azure with a scalable PostgreSQL database.

### 11. Conclusion
The DoPayments platform successfully demonstrates how modern web technologies and basic machine learning can be combined to solve traditional supply chain inefficiencies. By introducing structured financial planning alongside robust operational tools, the system provides a holistic solution for modern retail and distribution networks to achieve sustainable growth.

---
© 2026 DoPayments Project. All Rights Reserved.
