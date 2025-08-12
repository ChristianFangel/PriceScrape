# Competitor Pricing Monitor

## Overview

This is a Flask-based web scraper application that monitors competitor pricing data across multiple equity management and legal tech companies. The application provides a dashboard interface to view scraped pricing information and allows manual refresh of competitor data. It's designed to help track pricing strategies and market positioning by automatically extracting pricing information from competitor websites.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

**Web Framework**: Built with Flask as a lightweight Python web framework, suitable for the simple dashboard requirements and scraping operations.

**Frontend Architecture**: Uses server-side rendering with Jinja2 templates and Bootstrap for styling. The frontend consists of:
- Base template with dark theme Bootstrap CSS
- Dashboard interface showing competitor pricing cards
- Manual refresh functionality via POST requests
- Flash messaging for user feedback

**Scraping Engine**: Custom `CompetitorScraper` class that handles web scraping operations:
- Requests library for HTTP operations with browser-like headers
- BeautifulSoup for HTML parsing
- Trafilatura for content extraction
- In-memory data storage (no persistent database)
- Configurable competitor list with URLs and display names

**Data Management**: Uses in-memory storage for scraped data, meaning data is lost on application restart. This suggests the application is designed for real-time monitoring rather than historical analysis.

**Error Handling**: Implements comprehensive error handling with logging and user feedback through Flask's flash messaging system.

## External Dependencies

**Core Dependencies**:
- Flask - Web framework
- Requests - HTTP client for web scraping
- BeautifulSoup4 - HTML parsing
- Trafilatura - Content extraction

**Frontend Dependencies**:
- Bootstrap CSS (via CDN) - UI framework with dark theme
- Bootstrap Icons - Icon library
- Chart.js - Charting library (included but not actively used in visible code)

**Target Websites**: Currently configured to scrape pricing data from:
- Carta (carta.com)
- Bolago (bolago.com) 
- NVR (nvr.se)
- Ledgy (ledgy.com)
- Cake Equity (cakeequity.com)
- Mantle (withmantle.com)
- Clara (clara.co)

**Infrastructure**: Designed to run on Replit with ProxyFix middleware for proper header handling in the hosted environment.