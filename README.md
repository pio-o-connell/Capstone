# Harmonia

<img src="README-images/Features/HomePage-Part1.jpg" alt="Home page image" style="width:60%;">
<img src="README-images/Features/HomePage-Part2.jpg" alt="Home page image" style="width:60%;">


## OverView
<hr>

"Harmonia" is my capstone assessed portfolio project, developed as part of the Code Institute Full Stack Software Developer Bootcamp. 
This project showcases my skills in HTML5, CSS3, Bootstrap and Python with augmented AI to create a responsive, accessible website to -
 1. Promoting chemical free gardening and services available locally.
 2. A blog containing tips aimed at both amateur and professional to foster better practices and behaviours. 
  The name Harmonia is actually co-pilot inspired.
 3. Booking Services offered complete with costings 

The temporary live project can be found here: <a href="https://pio-o-connell.github.io/Individual/">Harmonia</a>

<h2 align="center" id="TOC">Index</h2>

- [Harmonia](#harmonia)
  - [OverView](#overview)
  - [UX Design Process](#ux-design-process)
    - [User Stories](#user-stories)
    - [Wireframes](#wireframes)
    - [Colour Scheme](#colour-scheme)
    - [Fonts](#fonts)
  - [Features](#features)
    - [Landing page](#landing-page)
    - [Login](#login)
    - [Register](#register)
    - [Logout](#logout)
    - [Blog CRUD](#blog-crud)
    - [Comment CRUD](#comment-crud)
    - [Services \\ Add To Cart](#services--add-to-cart)
    - [Booking](#booking)
    - [Administrator Page](#administrator-page)
  - [Improvements](#improvements)
  - [Deployment](#deployment)
  - [Testing and Validation](#testing-and-validation)
    - [HTML Validation](#html-validation)
    - [CSS Validation](#css-validation)
    - [Python Validation](#python-validation)
    - [JS Validation](#js-validation)
  - [AI Implementation](#ai-implementation)
  - [Database](#database)
  - [References](#references)
  - [Tech Employed](#tech-employed)
  - [Learning Points](#learning-points)
    - [Lighthouse](#lighthouse)
    - [Wave](#wave)
    - [Unit Testing Scripting](#unit-testing-scripting)
    - [Harmonia Application Testing Matrix](#harmonia-application-testing-matrix)

## UX Design Process
<details>
    <summary>Project Board
    </summary>
    <a href="https://github.com/users/pio-o-connell/projects/9">GitHub Project Board</a>

</details>


### User Stories
<details>
    <summary>Details
    </summary>

    1. Authentication & Profiles
       - As a SuperUser, I want to manage users, services, and bookings efficiently.
       - As a SuperUser, SuperUser, I can edit profiles so that I can keep user information up to date
       - As a SuperUser, I can moderate blogs and comment ensuring content both relevant and appropriate
       - As a User, As a User, I can succesfully log in so that so I can securely edit blogs/comments
       - As a Guest, I can register so that so I can securely edit contribute blogs/comments

    2. Blog Management
        - Registered User can create blogs adding to gardening knowledge pool
        - Guest can read all blogs 
        - Registered User can update their blogs
        - Registered User can delete their blogs


    3. Comment Management
        - Visiting guest can create comment adding to blog's knowledge pool
        - Visiting guest can read comment 
        - Returning visiting guest or registered User can update their comments
        - Returning visiting guest or registered User can delete their comments


    4. Shopping Cart / Booking creation
        - Visiting guest can create shopping cart persisted in stored cookies or session data. 
        - Visiting guest can create Booking to complete transaction . Information retrieved from stored cookies or session data.
        - Registered user can create shopping cart 
        - Registered user can create Booking to complete transaction . Information retrieved from Shopping Cart

    5. Booking Management
        - As a SuperUser,  I can approve bookings. Information retrieved from Bookings.




</details>

### Wireframes
 <details>
   <summary> Mobile pages logged in
   </summary>
  <img src="documentation/images/Balsamiq/Images/mobile-loggedin-all.png" alt="mobile pages"  style="width:60%;">
 </details>

<details>
    <summary> Mobile pages logged out
    </summary>
    <img src="documentation/images/Balsamiq/Images/mobile-loggedOut-all.png" alt="mobile pages" style="width:60%;">
</details>

<details>
    <summary> XL and Large Home Page
    </summary>
    <img src="documentation/images/Balsamiq/Images/HomePage-XL-large.png" alt="mobile pages" style="width:60%;">
</details>

<details>
    <summary> XL and Large Blog Page
    </summary>
    <img src="documentation/images/Balsamiq/Images/BlogPage-XL-large.png" alt="mobile pages" style="width:60%;">
</details>

<details>
    <summary> XL and Large Comments Page
    </summary>
    <img src="documentation/images/Balsamiq/Images/CommentPage-XL-Large.png" alt="mobile pages" style="width:60%;">
</details>

<details>
    <summary> XL Services Page
    </summary>
    <img src="documentation/images/Balsamiq/Images/XL-Services.png" alt="mobile pages" style="width:60%;">
</details>

<details>
    <summary> Large Services Page
    </summary>
    <img src="documentation/images/Balsamiq/Images/Large-Services.png" alt="mobile pages" style="width:60%;">
</details>

<details>
    <summary> Large and XL Booking Page
    </summary>
    <img src="documentation/images/Balsamiq/Images/XL-large-Booking.png" alt="mobile pages" style="width:60%;">
</details>

<details>
    <summary> Large and XL Registration Page
    </summary>
    <img src="documentation/images/Balsamiq/Images/XL-large-Registration.png" alt="mobile pages" style="width:60%;">
</details>

### Colour Scheme

<img src="documentation/images/SWATCH.jpg" alt="Image from which colour palette generated" style="width:60%;">

<details>
<summary>Colour Palette & Design Choices</summary>

I used one **PRIMARY** colour for all text, a **SECONDARY** colour for the Call to Action, and whitespace appropriately.  
The main page uses the **rule of thirds** for a balanced composition.  
Colours were selected using [Image Color Picker](https://imagecolorpicker.com/).

| Main Palette       | Hex       | Usage                                   |
|-------------------|-----------|----------------------------------------|
| Flax              | #E9D98A   | Background                              |
| Dark Moss Green   | #506D1B   | CTA / Secondary colour                  |
| Ecru              | #C9B66B   | Highlight links / hover effects         |
| Eggshell          | #E6E2D2   | Background areas or cards               |
| Davy’s Grey       | #4D4D4D   | Primary colour / text                   |

Accessibility checks were done with [Colour Contrast Checker](https://colourcontrast.cc/), [WebAIM](https://webaim.org/resources/contrastchecker/), and [Adobe Color](https://color.adobe.com/create/color-contrast-analyzer).

<details>
<summary>Click to view Colour Contrast Checker results</summary>
<img src="assets/documentation/images/testing/Color-contrast/Colorcontrastcc.jpg" alt="Colour contrast results" style="width:60%;">
[View live responsiveness](https://ui.dev/amiresponsive?url=https://pio-o-connell.github.io/Individual/index.html)
</details>

<details>
<summary>Click to view WebAIM results</summary>
<img src="assets/documentation/images/testing/Color-contrast/web-aim.jpg" alt="WebAIM contrast results" style="width:60%;">
[View live responsiveness](https://ui.dev/amiresponsive?url=https://pio-o-connell.github.io/Individual/index.html)
</details>

<details>
<summary>Click to view Adobe Color results</summary>
<img src="assets/documentation/images/testing/Color-contrast/adobe-color-analyzer.jpg" alt="Adobe Color contrast results" style="width:60%;">
[View live responsiveness](https://ui.dev/amiresponsive?url=https://pio-o-connell.github.io/Individual/index.html)
</details>

</details>



### Fonts
<details>
    <summary>Details
    </summary>
    Similar to colour, the font should be easy to read.<br> 
    Thus one font i.e. Inter is only necessary i.e. for titles, body, and a call to actiob(CTA).<br>    
    These were implemented through Google Fonts using a direct import code within the style.css file.<br>

    /_ Google fonts import _/ @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900&family=Macondo&display=swap');

</details>

[Back To Top](#harmonia)


## Features
--- 
<details>
    <summary>Details
    </summary>

        ### Landing page

        ### Login
                ### Admin Login

                ### User Login

        ### Register

        ### Logout

        ### Blog CRUD

        ### Comment CRUD

        ### Services \ Add To Cart

        ### Booking

        ### Custom Error pages

            #### 404 Page Not Found

            #### 403 Access Denied

            #### 500 Server Error



</details><br>

 ### Landing page
<details>
  <summary>Home Page</summary>
  There is a fold in the page by design <br>
  <img src="README-images/Features/HomePage-Part1.jpg" alt="Home page image" style="width:40%;">
  <img src="README-images/Features/HomePage-Part2.jpg" alt="Home page image" style="width:40%;">
</details>


 ### Login
<details>
  <summary>Login Page</summary>
  Login Page - There are four  types of user Admin, Customer, Blogger and Guests can browse <br><br>
  <img src="README-images/Features/CustomerLogin.jpg" alt="Login page image" style="width:40%;">
  <img src="README-images/Features/AdminScreen.jpg" alt="Login page image" style="width:40%;">
</details>

### Register
<details>
  <summary>Registration Page</summary>
  Login Page - A guest becomes a customer then a blogger after submitting a blog <br><br>
  <img src="README-images/Features/RegistrationPage.jpg" alt="Register page image" style="width:40%;">
  <img src="README-images/Features/email-sent.jpg" alt="Email page image" style="width:40%;">
</details>

### Logout
<details>
  <summary>Registration Page</summary>
  Login Page - Confirmation Logged out return to home page <br><br>
  <img src="README-images/Features/LoggedOut.jpg" alt="Guest\Customer Blog Page" style="width:30%;">
 
</details>

### Blog CRUD
<details>
  <summary>Blog Page</summary>
  A guest can create a blog by firstly submitting a test blog, <br>
  After creating the test blog, and to submit for approval the guest must register as a registered customer <br>
  There is no onus to purchase anything.<br>
  Subsequently if administrator approves, a customer becomes a registered blogger <br><br>
  A customer can create a blog but again requires Administrator approval before it is displayed <br>
  An administrator can (create,edit,delet) a blog<br>
  Only the admin can delete any blog, a blogger may (create,edit,delete) their own blogs <br>

  <img src="README-images/Features/BlogPage-Guest.jpg" alt="Guest\Customer Blog Page" style="width:30%;">
  <img src="README-images/Features/BlogPageBlogger.jpg" alt="Blogger Page" style="width:30%;">
  <img src="README-images/Features/MyBlogPostsBlogger.jpg" alt="Logged Out home page image" style="width:30%;">
</details>

### Comment CRUD
<details>
  <summary>Comment Page</summary>
  A guest can comment (create,edit,delete) on their comments  <br>
  A customer,fellow blogger and indeed the Admin can comment(create,edit,delete) on the blogs.<br>
   <br><br>

  <img src="README-images/Features/GuestAddCommentBefore.jpg" alt="Guest\Customer Blog Page" style="width:30%;">
  <img src="README-images/Features/GuestAddcommentAfter.jpg" alt="Blogger Page" style="width:30%;">
  <img src="README-images/Features/RegisteredAddComment.jpg" alt="Logged Out home page image" style="width:30%;">
</details>

### Services \ Add To Cart
<details>
  <summary>Services</summary>
  A guest, customer,blogger and admin can add 4 types of services to the cart  <br>
   <br><br>

  <img src="README-images/Features/Services-guest.jpg" alt="Guest Service Page" style="width:30%;">
  <img src="README-images/Features/Services-Shoppingcart-Guest.jpg" alt="Guest Services with shopping cart Page" style="width:30%;">
  <img src="README-images/Features/Services-Cart-Customer.jpg" alt="Customer Services with shopping cart" style="width:30%;">
</details>

### Booking
<details>
  <summary>Booking</summary>
  A guest, customer,blogger and admin perform a booking  <br>
  The guest will have to become a customer before the booking is complete >br> 
   <br><br>

  <img src="README-images/Features/BookingServicesGuest.jpg" alt="Guest completes transaction" style="width:40%;">
  <img src="README-images/Features/BookingCompleteGuest.jpg" alt="Guest confirmation" style="width:40%;">
  <img src="README-images/Features/BookingCustomer.jpg" alt="Customer completes transaction" style="width:40%;">
  <img src="README-images/Features/BookingCompleteCustomer.jpg" alt="Customer confirmation" style="width:40%;">
</details>

### Administrator Page
<details>
  <summary>Administation</summary>
  Administaror can monitor users, blogs & comments, services & bookings <br>
  This is veru useful for monitoring the site

  <img src="README-images/Features/AdminScreen.jpg" alt="Guest completes transaction" style="width:30%;">
  <img src="README-images/Features/AdminDashboard1.jpg" alt="Guest confirmation" style="width:60%;">
  
</details>








[Back To Top](#harmonia)

## Improvements
--- 
<details>
    <summary>Details
    <img src="assets/documentation/images/testing/Color-contrast/Colorcontrastcc.jpg" alt="Colour contrast results" style="width:60%;">
    [Click to view live responsiveness](https://ui.dev/amiresponsive?url=https://pio-o-connell.github.io/Individual/index.html)  
</details><br>

[Back To Top](#harmonia)

## Deployment
---
<details>
    <summary>Details
    </summary>
    
      This [GitHub](https://github.com/) project was created using the [Code Institute Template](https://github.com/Code-Institute-Org/ci-full-template) ensuring all necessary dependencies.

      Setup a repo using this method and template:

            1. Login to your GitHub profile.
            2. Navigate to the Code Institute Full Template
            3. Click the dropdown for 'Use this template' and select "Create a new repository"
            4. Generate the necessary name and description for your repo and click 'Create repository from template'
            5. Navigate to the new repo and click the green 'Open' button with the Gitpod logo<br>
              **IMPORTANT - This button should only be clicked once to generate the new IDE workspace**
            6. You can now work on your repository within the Code Institute Gitpod IDE workspace
    
            Once the project repo is created, an early deployment for the live project should performed.<br>
            This allows for early and continuous testing using a variety of devices, as well as the Dev Tools available within browsers.

            Additional information on the deployment process can be found on the official [GitHub Docs](https://docs.github.com/en/pages/quickstart)

</details>



[Back To Top](#harmonia)

## Testing and Validation
---


  

  ### HTML Validation
 <details>
  <summary>HTML</summary>
   The HTML was checked using the w3C markup validation service 0 errors found on home page.<br><br>
  <img src="README-images/Testing&Validation/html-validator/HTMLValidator-HomePage.png" alt="HTML W3C Results" style="width:30%;">
  <img src="README-images/Testing&Validation/html-validator/HTMLValidator-BlogPage.png" alt="HTML W3C Results" style="width:30%;">
  <img src="README-images/Testing&Validation/html-validator/HTMLValidator -Services.png" alt="HTML W3C Results" style="width:30%;">
  <img src="README-images/Testing&Validation/html-validator/HTMLValidator-Bookings.png" alt="HTML W3C Results"" style="width:30%;">
  <img src="README-images/Testing&Validation/html-validator/HTMLValidator-Register.png" alt="HTML W3C Results" style="width:30%;">
  
</details>

  

  ### CSS Validation
  
<details>
  <summary>CSS</summary>
  The CSS was checked using the W3C validation service 0 errors found (only vendor-prefix warnings for `-ms-flexbox`, `-webkit`, etc.).<br>
  <img src="README-images/Testing&Validation/CSS/HomePage-stylesheet.png" alt="CSS Jigsaw Results" style="width:30%;">
</details>

  ### Python Validation
 
 <details>
  <summary>Python</summary>
   All apps were checked using Flake8 tool to comply with PEP 8 standard<br><br>
  <img src="README-images/Testing&Validation/Pep8-using-flake8/Pep9 results .png" alt="PEP 8 conformance" style="width:30%;">
</details>

  ### JS Validation
 <details>
  <summary>Javascript</summary>
   All Main page was checked using JSHint tool <br>
   JSHint conforms to configurable JavaScript rules and ECMAScript versions rather than a single standard<br>
  <img src="README-images/Testing&Validation/JSHint/AdminPage-JSHint.jpg" alt="Javascript conformance" style="width:30%;">
  <img src="README-images/Testing&Validation/JSHint/BlogPage-JSHinr.jpg" alt="Javascript conformance" style="width:30%;">
  <img src="README-images/Testing&Validation/JSHint/Services-JSLint.jpg" alt="Javascript conformance" style="width:30%;">
  <img src="README-images/Testing&Validation/JSHint/Bookings-JSHint.jpg" alt="Javascript conformance" style="width:30%;">
  <img src="README-images/Testing&Validation/JSHint/Login-JSHint.jpg" alt="Javascript conformance" style="width:30%;">
  <img src="README-images/Testing&Validation/JSHint/register-jshint.jpg" alt="Javascript conformance" style="width:30%;">

</details>



[Back To Top](#harmonia)

## AI Implementation
--- 
<details>
    <summary>Details</summary>

    ### Code Creation

    ### Debugging

    ### Performance and Experience

    ### Development Process
    
    
    
    <img src="assets/documentation/images/testing/Color-contrast/Colorcontrastcc.jpg" alt="Colour contrast results" style="width:60%;">
    [Click to view live responsiveness](https://ui.dev/amiresponsive?url=https://pio-o-connell.github.io/Individual/index.html)  
</details>

[Back To Top](#harmonia)

## Database
--- 
<details>
    <summary>Details
    </summary>
    The database is a Postgres database hosted by Code institute

    ![alt text](documentation\images\databaseImage.png)
  <img src="documentation\images\databaseImage.png" alt="Colour contrast results" style="width:40%;">
   
</details>


[Back To Top](#harmonia)



## References
--- 
<details>
<summary>Details</summary>

  <h4>Documentation</h4>
  <ul>
      <li>
          <a href="https://docs.djangoproject.com/en/5.2/ref/models/querysets/" target="_blank">
              Django documentation – very useful for several sections
          </a>
      </li>
  </ul>

  <h4>W3Schools</h4>
  <ul>
      <li>
          <a href="https://www.w3schools.com/python/python_lists_comprehension.asp" target="_blank">
              Reminder on how list comprehension works
          </a>
      </li>
  </ul>

  <h4>Old Projects</h4>
  <ul>
      <li>
          <a href="https://github.com/pio-o-connell/Individual" target="_blank">
              GitHub – Older project reference
          </a>
      </li>
  </ul>

</details>
    

[Back To Top](#harmonia)

## Tech Employed
--- 
<details>
  <summary>Technologies and Languages</summary>

  <h3>Languages</h3>
  <img src="https://img.shields.io/badge/HTML5-Language-grey?logo=html5&logoColor=%23ffffff&color=%23E34F26" alt="HTML5 badge">
  <img src="https://img.shields.io/badge/CSS3-Language-grey?logo=css3&logoColor=%23ffffff&color=%231572B6" alt="CSS3 badge">
  <img src="https://img.shields.io/badge/javascript-Language-blue?logo=javascript&logoColor=%23ffffff&color=%23E34F26" alt="javascript badge">
  <img src="https://img.shields.io/badge/Python-3.12.8-grey?logo=python&logoColor=%23ffffff&color=%233776AB" alt="Python badge">

  <h3>Libraries and Frameworks</h3>
  <a href="https://getbootstrap.com/"><img src="https://img.shields.io/badge/Bootstrap-v5.3.3-grey?logo=bootstrap&logoColor=%23ffffff&color=%237952B3" alt="Bootstrap" ></a>
    <a href="https://getbootstrap.com/"><img src="https://img.shields.io/badge/Font_Awesome-Icons-grey?logo=fontawesome&logoColor=%23ffffff&color=%23538DD7" alt="Font Awesome"></a>
    <a href="https://getbootstrap.com/"><img src="https://img.shields.io/badge/Google_Fonts-Fonts-grey?logo=googlefonts&logoColor=%23ffffff&color=%234285F4" alt="Google Fonts"></a>


  <h3>Tools and Programs</h3>
  <img src="https://img.shields.io/badge/Balsamiq-Wireframes-grey?logoColor=%23ffffff&color=%23CC0100" alt="Balsamiq badge">
  <img src="https://img.shields.io/badge/Git-v2.51.0-grey?logo=git&logoColor=%23ffffff&color=%23F05032" alt="Git">
  <img src="https://img.shields.io/badge/GitHub-Repo_Hosting-white?logo=github&logoColor=%23ffffff&color=%23181717 " alt="Git hosting">
    <img src="https://img.shields.io/badge/Microsoft-Copilot-5E5E5E?style=flat-square&logo=microsoft&logoColor=white&color=0078D4" alt="Microsoft Copilot">
    <img src="https://img.shields.io/badge/ChatGPT-00A67E?style=flat-square&logo=openai&logoColor=white&color=00A67E" alt="ChatGPT">
    <img src="https://img.shields.io/badge/GitHub_Copilot-181717?logo=githubcopilot&logoColor=white&color=1B1F23" alt="GitHub Copilot">
    <a href="https://figma.com"><img src="https://img.shields.io/badge/Figma-green" alt="Figma"></a>
    <a href="https://squoosh.app">
    <img src="https://img.shields.io/badge/Squoosh-squoosh.app-0b69ff?style=for-the-badge" alt="Squoosh">
    </a>
</details>

[Back To Top](#harmonia)
## Learning Points
--- 
<details>
    <summary>Details
    </summary>
    <img src="assets/documentation/images/testing/Color-contrast/Colorcontrastcc.jpg" alt="Colour contrast results" style="width:60%;">
    [Click to view live responsiveness](https://ui.dev/amiresponsive?url=https://pio-o-connell.github.io/Individual/index.html)  
</details>

[Back To Top](#harmonia)



  
  ### Lighthouse
  ### Wave
  ### Unit Testing Scripting
  ### Harmonia Application Testing Matrix