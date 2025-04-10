// Load up all sections in the sidebar: 
function loadSectionsInSidebar(sections, spContentsId) {
    // <label for="vegetables" style="word-wrap:break-word" onclick="toggle()">
    // <input id="vegetables" type="checkbox" value="vegetables">Vegetables
    // </label><br>
    for(section of sections) {

        const identifier = section.sectionIdentifier + "_sidebar";

        const label = document.createElement("label");
        label.htmlFor = identifier;
        label.style = "word-wrap:break-word";
        label.onclick=toggle;

        const input = document.createElement("input");
        input.id = identifier;
        input.type = "checkbox";
        input.value = section.sectionIdentifier;

        textNode = document.createTextNode(section.sectionName);
        label.appendChild(input);
        label.appendChild(textNode);
        document.getElementById(spContentsId).appendChild(label);
        document.getElementById(spContentsId).appendChild(document.createElement("br"));
    }
    
}

function loadSectionTables(sections, mainDivId) {
    for(section of sections) {

        const sectionTableClass = section.sectionIdentifier + "_table";

        // <h2 class="vegetables_table center">Vegetables</h2>
        const h2 = document.createElement("h2");
        h2.classList.add(...[sectionTableClass, "center"]);
        const h2Text = document.createTextNode(section.sectionName);
        h2.appendChild(h2Text);
        document.getElementById(mainDivId).appendChild(h2);

        // <table id="vegetables_table" class="vegetables_table itemTable center">
        const table = document.createElement("table");
        table.classList.add(...[sectionTableClass, "itemTable", "center"]);
        table.id = sectionTableClass;
        document.getElementById(mainDivId).appendChild(table);

        // <tr> header: 
        const tr1 = document.createElement("tr");

        const th1 = document.createElement("th");
        th1.appendChild(document.createTextNode("Item Picture"));
        const th2 = document.createElement("th");
        th2.appendChild(document.createTextNode("Item Name"))
        const th3 = document.createElement("th");
        th3.appendChild(document.createTextNode("Price"))
        const th4 = document.createElement("th");
        th4.appendChild(document.createTextNode("Stock"))
        const th5 = document.createElement("th");
        th5.appendChild(document.createTextNode("Amount in Cart"))

        tr1.appendChild(th1);
        tr1.appendChild(th2);
        tr1.appendChild(th3);
        tr1.appendChild(th4);
        tr1.appendChild(th5);
        table.appendChild(tr1);

    }
}

function loadSectionContents(sections) {
    for(section of sections) {
        for(sectionInventory of section.inventory) {
            appendRow(section.sectionIdentifier + "_table", sectionInventory);
        }
    }
}

function appendRow(tableID, itemObj) {

    const tableRow = document.createElement("tr");

    // <td>
    // <img src="./images/apple.png" />
    // </td>
    const tdImage = document.createElement("td");
    const img = document.createElement("img");
    img.src = itemObj.imgPath;
    tdImage.appendChild(img);
    tableRow.appendChild(tdImage);

    // <td>Item Name</td>
    const tdName = document.createElement("td");
    const tdNameText = document.createTextNode(itemObj.name);
    tdName.appendChild(tdNameText);
    tableRow.appendChild(tdName);

    // <td>$0.50</td>
    const tdPrice = document.createElement("td");
    const tdPriceText = document.createTextNode("$" + itemObj.price.toFixed(2));
    tdPrice.appendChild(tdPriceText);
    tableRow.appendChild(tdPrice);

    // <td>Stock</td>
    const difference = itemObj.current_stock - itemObj.in_cart;
    const final_stock = (difference == 0) ? "Sold out" : difference;
    const tdStock = document.createElement("td");
    const tdStockText = document.createTextNode(final_stock.toString());
    tdStock.id = itemObj.name + "_current_stock";
    tdStock.appendChild(tdStockText);
    tableRow.appendChild(tdStock);

    // <td class="item_selection">
    const tdItemSelect = document.createElement("td");

    // <p id="plus_apple" class="plus">+</p>
    const plus = document.createElement("p");
    const plusText = document.createTextNode("+");
    plus.className = "plus";
    plus.appendChild(plusText);
    tdItemSelect.appendChild(plus);
    plus.addEventListener('click', () => {
        modifyCart(itemObj, true);
    });
    tdItemSelect.appendChild(plus);

    // <p class="amount">0</p>
    const amount = document.createElement("p");
    const amountText = document.createTextNode((itemObj.in_cart).toString());
    amount.appendChild(amountText);
    amount.className = "amount";
    amount.id = itemObj["name"] + "_amount";
    tdItemSelect.appendChild(amount);

    // <p id="minus_amount" class="minus">–</p>
    const minus = document.createElement("p");
    const minusText = document.createTextNode("-");
    minus.className = "minus";
    minus.appendChild(minusText);
    tdItemSelect.appendChild(minus);
    minus.addEventListener('click', () => {
        modifyCart(itemObj, false);
    });
    tdItemSelect.appendChild(minus);

    tableRow.appendChild(tdItemSelect);

    document.getElementById(tableID).appendChild(tableRow);
}

const modifyCart = (itemObj, increment) => {

    let inCart = itemObj.in_cart;
    let currentStock = itemObj.current_stock;

    if(increment) {
        inCart = (inCart + 1) < currentStock ? inCart + 1 : currentStock;
    }
    else {
        inCart = Math.max(inCart-1, 0);
    }

    if(inCart >= currentStock) {
        document.getElementById(itemObj.name + "_current_stock").innerHTML = "Sold out";
    }
    else {
        document.getElementById(itemObj.name + "_current_stock").innerHTML = (currentStock - inCart).toString();
    }

    document.getElementById(itemObj.name + "_amount").innerHTML = inCart.toString();

    itemObj.in_cart = inCart;
    itemObj.current_stock = currentStock;

}

function toggle() {

    if(document.getElementById("show_all").checked) {
        for(element of document.getElementById("spContents").getElementsByTagName('input')) {
            for(e of document.getElementsByClassName(element.defaultValue + "_table")) {
                e.style.display = "block";
            }
        }
    }
    else {
        for(element of document.getElementById("spContents").getElementsByTagName('input')) {
            const check_name = element.defaultValue;
            const checked = element.checked;
        
            if(check_name === "show_all") {
                continue;
            }
            else {
                if(!checked) {
                    for(e of document.getElementsByClassName(check_name + "_table")) {
                        e.style.display = "none";
                    }
                }
                else {
                    for(e of document.getElementsByClassName(check_name + "_table")) {
                        e.style.display = "block";
                    }
                }
                
            }
        }
    }
    
}