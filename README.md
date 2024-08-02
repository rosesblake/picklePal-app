# PicklePal App

## Wireframes

**figma**
https://www.figma.com/design/J4mKwxV0URjaOAYCcCaals/PicklePal?node-id=0-1&m=dev

## Description

PicklePal is a mobile and web application designed to help pickleball players connect, schedule games, and form groups based on their location. The app features a social feed for users to share updates, achievements, and game highlights.

## Stack

- **Frontend:** HTML, CSS, JavaScript, Tailwind CSS
- **Backend:** Python/Flask
- **Database:** PostgreSQL
- **APIs:** Custom API, Maps API

## Focus

This will be a full-stack application with an even focus on both the front-end UI and the back-end functionality.

## Type

The project will be developed as both a website and a mobile app to maximize accessibility and user engagement.

## Goal

The primary goal of PicklePal is to enable pickleball players to easily find partners, schedule games, and connect with others in their area. It aims to foster a sense of community among players by providing a platform to connect, share updates, and organize games.

## Users

The target users are pickleball players of all skill levels who want to connect with others in their area. This includes solo players, groups, and teams who wish to schedule and participate in pickleball games.

## Data

- **Map API Data:** Used to determine player locations and nearby pickleball courts.
- **Custom API Data:** Used to manage user profiles, group formations, courts, messages, and social feed content.

### Database Schema

- **Users:**
  - id, profile_image, password, first_name, last_name, email, city, state, zip_code, skill, home_court_id (FK)
- **Courts:**
  - id, name, address, city, state, zip_code
- **Groups:**
  - id, name, description, owner_id (FK)
- **GroupMemberships:**
  - group_id (FK), user_id (FK)
- **Posts:**
  - id, user_id (FK), court_id (FK), content, timestamp
- **Likes:**
  - id, post_id (FK), user_id (FK)
- **Comments:**
  - id, post_id (FK), user_id (FK), content, timestamp
- **Friends:**
  - user_id (FK), friend_id (FK), status
- **Messages:**
  - id, sender_id (FK), receiver_id (FK), content, timestamp
- **Reviews:**
  - id, court_id (FK), user_id (FK), content, rating

### API Issues

- **Data Consistency:** Ensuring data from the Maps API is accurate and up-to-date.
- **Rate Limits:** Managing API usage within the limits of free or paid plans.
- **Data Security:** Ensuring user data is securely transmitted and stored.

### Security

- **User Authentication:** Secure login and registration processes.
- **Data Encryption:** Encrypt sensitive data such as passwords.
- **API Security:** Protecting custom API endpoints from unauthorized access.

### MVP

- **Location-Based Matchmaking:** Finding nearby players and courts using the Maps API.
- **Group Formation:** Creating and managing groups.
- **Social Feed:** Sharing updates, achievements, and game highlights.

### Extra

- **Review Feature:** Adding reviews for courts.
- **Spectator Feature:** Allowing users to follow games as spectators.

## User Flow

1. **Registration/Login:** Users create an account or log in.
2. **Profile Setup:** Users set up their profile, including location, name, skill level, and home court.
3. **Finding Courts:** Users search for nearby pickleball courts using the Maps API.
4. **Joining/Creating Groups:** Users form or join groups.
5. **Social Interaction:** Users post updates and interact on the social feed.

## Future Goals

- **Machine Learning:** Suggesting optimal game times and partners based on user activity.
- **Tournament Management:** Organizing and managing local tournaments.
- **Performance Tracking:** Recording and analyzing game performance statistics.
