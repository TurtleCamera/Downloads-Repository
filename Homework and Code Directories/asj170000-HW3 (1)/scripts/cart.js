// Load up all sections in the sidebar: 
function loadSectionsInSidebar(sections, discounts) {
    // <label for="vegetables" style="word-wrap:break-word" onclick="toggle()">
    // <input id="vegetables" type="checkbox" value="vegetables">Vegetables
    // </label><br>

    const topPage = document.createElement("a");
    topPage.href = "#"

    text = document.createTextNode("Top of the page");
    topPage.appendChild(text);
    document.getElementById("spContents").appendChild(topPage);
    document.getElementById("spContents").appendChild(document.createElement("br"));

    for(section of sections) {
        let a = document.createElement("a");
        a.href = "#" + section.sectionIdentifier + "_table";

        text = document.createTextNode(section.sectionName);
        a.appendChild(text);
        document.getElementById("spContents").appendChild(a);
        document.getElementById("spContents").appendChild(document.createElement("br"));
    }

    let a = document.createElement("a");
    a.href = "#special_offers_table";

    if(discounts.length > 0) {
        text = document.createTextNode("Special Offers");
        a.appendChild(text);
        document.getElementById("spContents").appendChild(a);
        document.getElementById("spContents").appendChild(document.createElement("br"));
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
        th3.appendChild(document.createTextNode("Total Price"))
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

function loadSpecialOffersSection(discounts, mainDivId) {

    if(discounts.length === 0) {
        return;
    }

    const discountTableClass = "special_offers_table";

    // <h2 class="vegetables_table center">Vegetables</h2>
    const h2 = document.createElement("h2");
    h2.classList.add(...[discountTableClass, "center"]);
    const h2Text = document.createTextNode("Special Offers & Discounts");
    h2.appendChild(h2Text);
    document.getElementById(mainDivId).appendChild(h2);

    // <table id="vegetables_table" class="vegetables_table itemTable center">
    const table = document.createElement("table");
    table.classList.add(...[discountTableClass, "itemTable", "center"]);
    table.id = discountTableClass;
    document.getElementById(mainDivId).appendChild(table);

    // <tr> header: 
    const tr1 = document.createElement("tr");

    const th1 = document.createElement("th");
    th1.appendChild(document.createTextNode("Discount Name"));
    const th2 = document.createElement("th");
    th2.appendChild(document.createTextNode("Percentage Discount"))
    const th3 = document.createElement("th");
    th3.appendChild(document.createTextNode("Flat Discount"))

    tr1.appendChild(th1);
    tr1.appendChild(th2);
    tr1.appendChild(th3);
    table.appendChild(tr1);


    for(discount of discounts) {
        appendDiscountRow(table.id, discount)
    }
}

function appendDiscountRow(tableID, discountObj) {

    const tableRow = document.createElement("tr");

    const tdName = document.createElement("td");
    const tdNameText = document.createTextNode(discountObj.discountName);
    tdName.appendChild(tdNameText);
    tableRow.appendChild(tdName);

    const discountPercent = discountObj.percentDiscount;
    const tdPercentDiscount = document.createElement("td");
    const tdPercentDiscountText = document.createTextNode(discountPercent === 0 ? "Not applicable" : "+" + discountPercent.toFixed(2) + "% off");
    tdPercentDiscount.appendChild(tdPercentDiscountText);
    tableRow.appendChild(tdPercentDiscount);

    const flatDiscount = discountObj.flatDiscount;
    const tdFlatDiscount = document.createElement("td");
    const tdFlatDiscountText = document.createTextNode(flatDiscount === 0 ? "Not applicable" : "$" + flatDiscount.toFixed(2) + " off");
    tdFlatDiscount.appendChild(tdFlatDiscountText);
    tableRow.appendChild(tdFlatDiscount);

    document.getElementById(tableID).appendChild(tableRow);
}

function loadSectionContents(sections) {
    for(section of sections) {
        for(sectionInventory of section.inventory) {
            appendRow(section.sectionIdentifier + "_table", sectionInventory);
        }
    }

}

function displayTotalPrice(pageSections) {

    const div = document.createElement("div");
    div.id = "final_price";

    let price = 0;
    for(section of pageSections) {
        for(item of section.inventory) {
            price += item.price * item.in_cart;
        }
    }

    if(discounts.length > 0) {
        const prediscount = document.createElement("h1");
        prediscount.className = "center";
        prediscount.innerHTML = "Price Pre-Discount: $" + price.toFixed(2);
        div.appendChild(prediscount);
    }

    let discountedPrice = price;
    
    let discountPercent = 0;
    for(discount of discounts) {
        discountedPrice -= discount.flatDiscount;
        discountPercent += discount.percentDiscount;
    }

    discountedPrice = discountedPrice - (discountedPrice * (discountPercent / 100.0) );
    discountedPrice = discountedPrice < 0 ? 0 : discountedPrice;

    const finalPrice = document.createElement("h1");
    finalPrice.className = "center";
    finalPrice.innerHTML = pageSections.length > 0 ? "Final Price: $" + discountedPrice.toFixed(2) : "Your cart is empty.";

    div.appendChild(finalPrice);

    if(discounts.length > 0) {
        const discount = document.createElement("h2");
        discount.className = "center";
        discount.innerHTML = "You saved: $" + (price - discountedPrice).toFixed(2);
        div.appendChild(discount);
    }

    div.appendChild(document.createElement("br"));

    document.getElementById("final_price")?.remove();
    document.getElementById("mainId").appendChild(div);

}

// Keep all search params: 
[...document.querySelectorAll('a')].forEach(e=>{
    const url = new URL(e.href)
    for (let [k,v] of new URLSearchParams(window.location.search).entries()) {
        url.searchParams.set(k,v)
    }
    e.href = url.toString();
});

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
    const tdPriceText = document.createTextNode("$" + (itemObj.price * itemObj.in_cart).toFixed(2));
    tdPrice.id = itemObj.name + "_total_price";
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
    // const plus = document.createElement("p");
    // const plusText = document.createTextNode("+");
    // plus.className = "plus";
    // plus.appendChild(plusText);
    // tdItemSelect.appendChild(plus);
    // plus.addEventListener('click', () => {
    //     modifyCart(itemObj, true);
    // });
    // tdItemSelect.appendChild(plus);

    // <p class="amount">0</p>
    const amount = document.createElement("p");
    const amountText = document.createTextNode((itemObj.in_cart).toString());
    amount.appendChild(amountText);
    amount.className = "amount";
    amount.id = itemObj["name"] + "_amount";
    tdItemSelect.appendChild(amount);

    // <p id="minus_amount" class="minus">–</p>
    // const minus = document.createElement("p");
    // const minusText = document.createTextNode("-");
    // minus.className = "minus";
    // minus.appendChild(minusText);
    // tdItemSelect.appendChild(minus);
    // minus.addEventListener('click', () => {
    //     modifyCart(itemObj, false);
    // });
    // tdItemSelect.appendChild(minus);

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

    document.getElementById(itemObj.name + "_total_price").innerHTML = "$" + (inCart * itemObj.price).toFixed(2);

    displayTotalPrice(pageSections);

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

function readSections(pageSections) {
    for(key of Object.keys(localStorage)) {

        if(key === "sanity_check" || key === "specialty_quiz") {
            continue;
        }

        try {
            // let sections = JS/ON.par/se(localStorage.getItem(key));
            let sections = parseSectionString(localStorage.getItem(key));

            items = [];
            for(s of sections) {
                for(item of s.inventory) {

                    if(item.in_cart > 0) {
                        items.push(item);
                    }
                    
                }
            }

            if(items.length > 0) {
                pageSections.push({
                    "sectionName": key,
                    "sectionIdentifier": key.toLowerCase().replaceAll(" ", "_"),
                    "inventory": items
                });
            }

            
        }
        catch(ignored) {
            console.log(ignored);
        }
    }
}