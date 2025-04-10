function loadSectionTables(sections, mainDivId) {
    for(section of sections) {

        const sectionTableClass = section.sectionIdentifier + "_table";

        // <h2 class="vegetables_table center">Vegetables</h2>
        const h2 = document.createElement("h1");
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
        //document.getElementById(itemObj["name"] + "_current_stock").innerHTML = currentStock.toString();
        document.getElementById(itemObj.name + "_current_stock").innerHTML = (currentStock - inCart).toString();
    }

    document.getElementById(itemObj.name + "_amount").innerHTML = inCart.toString();

    itemObj.in_cart = inCart;
    itemObj.current_stock = currentStock;

}

const filter = (e) => {

    const text = e.target.value;

    if(/\d/.test(text)) {
        document.getElementById("results_text").innerHTML = "Search cannot contain #s.";
        return;
    }

    let numResults = 0;

    for(section of pageSections) {
        const tableRows = document.getElementById(section.sectionIdentifier + "_table").getElementsByTagName("tr");
        
        for(let x=1; x<tableRows.length; x++) {
            const itemName = tableRows[x].getElementsByTagName("td")[1].innerHTML;

            if(text.length === 0 || itemName.toLowerCase().includes(text.toLowerCase())) {
                tableRows[x].style.display = "table-row";
                numResults++;
            }
            else {
                tableRows[x].style.display = "none";
            }

        }

    }
    
    if(text.length === 0) {
        document.getElementById("results_text").innerHTML = "Type anything to search.";
    }
    else {
        if(numResults === 0) {
            document.getElementById("results_text").innerHTML = "No results.";
        }
        else {
            document.getElementById("results_text").innerHTML = "Found " + numResults + " item" + (numResults > 1 ? "s" : "") + ".";
        }
    }
    
}

function addListeners() {
    const search_box = document.getElementById('search_box');
    search_box.addEventListener('input', filter);
    search_box.addEventListener('propertychange', filter);
}