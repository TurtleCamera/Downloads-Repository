function takeQuiz() {
    currentQuestionIndex = 0;
    mcAnswers = [];
    timeStarted = new Date();
    document.getElementById("take_quiz_button").remove();
    displayQuestion(mcQuestions[currentQuestionIndex], currentQuestionIndex);
}

function skipButton() {
    mcAnswers.push(-1);
    currentQuestionIndex++;

    if(currentQuestionIndex >= mcQuestions.length) {
        displayResults();
    }
    else {
        displayQuestion(mcQuestions[currentQuestionIndex], currentQuestionIndex);
    }
}

function displayResults() {

    const discounts = [];

    document.getElementById("quiz").innerHTML = "";
    const endTime = new Date();
    const timeDiff = new Date(endTime - timeStarted).toISOString().slice(11,19);

    const qualify1 = mcAnswers[0] == 0;
    const qualify2 = mcAnswers[1] == 0;
    const qualify3 = mcAnswers[2] >= 2;

    let h1 = document.createElement("h1");
    h1.className = "center";
    h1.innerText = "Questionnaire Complete: (" + timeDiff + ")";
    document.getElementById("quiz").appendChild(h1);

    if(!qualify1 && !qualify2 && !qualify3) {
        let h1 = document.createElement("h1");
        h1.className = "center";
        h1.innerText = "You do not qualify for any special deals.";
        document.getElementById("quiz").appendChild(h1);
    }
    else {
        let h1 = document.createElement("h1");
        h1.className = "center";
        h1.innerText = "You qualify for the following deal(s):";
        document.getElementById("quiz").appendChild(h1);
    }

    if(qualify1) {
        let h1 = document.createElement("h1");
        h1.className = "center";
        h1.innerText = "Student discount: 15% off for being a student.";
        document.getElementById("quiz").appendChild(h1);
        discounts.push({
            discountName: "Student discount",
            percentDiscount: 15,
            flatDiscount: 0
        });
    }

    if(qualify2) {
        let h1 = document.createElement("h1");
        h1.className = "center";
        h1.innerText = "Low income: 50% off purchases.";
        document.getElementById("quiz").appendChild(h1);
        discounts.push({
            discountName: "Low income discount",
            percentDiscount: 50,
            flatDiscount: 0
        });
    }

    if(qualify3) {
        let h1 = document.createElement("h1");
        h1.className = "center";
        h1.innerText = "Supporter discount: $100 off next purchase for supporting >7 people.";
        document.getElementById("quiz").appendChild(h1);
        discounts.push({
            discountName: "Supporter discount",
            percentDiscount: 0,
            flatDiscount: 100
        });
    }

    let builder = "";

    for(let discount of discounts) {
        builder = builder + discount.discountName + "," + discount.percentDiscount + "," + discount.flatDiscount + "\n";
    }

    builder = builder.trim();

    if(builder.length > 0) {
        window.localStorage.setItem("specialty_quiz", builder.trim());
    }

    // window.localStorage.setItem("specialty_quiz", JS/ON.string/ify(discounts));

}

function nextButton() {
    const answerChoices = document.getElementsByName("answer");
    let selected = null;

    for(var x = 0; x < answerChoices.length; x++) {
        if(answerChoices[x].checked){
            selected = answerChoices[x].value;
        }
    }

    if(!selected) {
        document.getElementById("warning").innerHTML = "You must select an answer or skip the question.";
    }
    else {
        mcAnswers.push(selected);
        currentQuestionIndex++;

        if(currentQuestionIndex >= mcQuestions.length) {
            displayResults();
        }
        else {
            displayQuestion(mcQuestions[currentQuestionIndex], currentQuestionIndex);
        }

    }
}

function displayQuestion(questionObj, index) {
    document.getElementById("quiz").style.display = "block";

    answer_choices_div = document.getElementById("answer_choices");
    answer_choices_div.innerHTML = "";

    document.getElementById("question").innerHTML = questionObj.question;

    for(let x=0; x<questionObj.answer_choices.length; x++) {

        const answerChoice = questionObj.answer_choices[x];
        // <input type="radio" id="c1" name="answer" value="c1">
        // <label id="answer_1" class="answer_choices" for="c1">Label</label><br>
        const input = document.createElement("input");
        input.type = "radio";
        input.id = "c" + x;
        input.value = x.toString();
        input.name = "answer";

        answer_choices_div.appendChild(input);

        const label = document.createElement("label");
        label.id = "answer_" + x;
        label.className = "answer_choices";
        label.htmlFor = "c" + x;
        
        label.appendChild(document.createTextNode(answerChoice));

        answer_choices_div.appendChild(label);
        answer_choices.append(document.createElement("br"));
    }

    document.getElementById("warning").innerHTML = "Question " + (index + 1);

}