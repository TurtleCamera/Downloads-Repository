function helper() {
    console.log("called: " + validateForm());
}

function validateForm() {

    const firstName = document.forms["contactUsForm"]["fname"].value;
    const lastName = document.forms["contactUsForm"]["lname"].value;
    const phone = document.forms["contactUsForm"]["phone"].value;
    const email = document.forms["contactUsForm"]["email"].value;
    const comment = document.forms["contactUsForm"]["comment"].value;
    const gender = document.forms["contactUsForm"]["gender"].value;

    // The first name and last name should be alphabetic only
    if(!/^[a-zA-Z]+$/.test(firstName) || !/^[a-zA-Z]+$/.test(lastName)) {
        displayMessage("Your first and last name must be alphabetic.", true);
        return false;
    }
    // The first letter of first name and last name should be capital
    else if(
        !(firstName && firstName.length >= 1 && firstName[0] === firstName[0].toUpperCase() && 
        lastName && lastName.length >= 1 && lastName[0] === lastName[0].toUpperCase())
    ) {
        displayMessage("First letter of your first/last name should be capitalized.", true);
        return false;
    }
    // The first name and the name name can not be the same
    else if(firstName === lastName) {
        displayMessage("Your first name and last name cannot be the same.", true);
        return false;
    }
    // Phone number must be formatted as (ddd) ddd-dddd
    else if(!/^\(\d{3}\) \d{3}-\d{4}$/.test(phone)) {
        displayMessage("Your phone number must be in the format (ddd) ddd-dddd", true);
        return false;
    }
    // Email address must contain @ and .
    else if(!(email && email.includes("@") && email.includes("."))) {
        displayMessage("Your email address must contain @ and .", true);
        return false;
    }
    // Gender must be selected
    else if(!gender || gender.length === 0) {
        displayMessage("You must select a gender.");
        return false;
    }
    // The comment must be at least 10 characters
    else if(!comment || comment.length < 10) {
        displayMessage("Your comment must be at least 10 characters.", true);
        return false;
    }

    document.getElementById("form_message").innerHTML = "";
    const form1 = document.getElementById("contactUsForm");
    form1.style.display = "none";
    document.getElementById("form_message").innerHTML = "Thank you for contacting us. Your message has been submitted.";
    document.getElementById("form_message").style.color = "green";
    setTimeout(() => form1.submit(), 4000);

    return true;
}

function displayMessage(message, red) {
    document.getElementById("form_message").innerHTML = message;
    document.getElementById("form_message").style.color = red ? "red" : "black";
}