// Set the date constantly: 
const dateLoop = () => {
    const date = new Date();
    document.getElementsByClassName("storeLogo")[0].getElementsByTagName("h2")[0].innerHTML = date.toLocaleString();
}

function addSaveHook(pageSections, sectionName) {
    window.onbeforeunload = function() {
        try {
            // window.localStorage.setItem(sectionName, JS/ON.string/ify(pageSections));

            let string_builder = "";
            for(section_a of pageSections) {
                string_builder = string_builder + section_a.sectionName + "~" + section_a.sectionIdentifier + "~";
                
                for(item_a of section_a.inventory) {
                    string_builder = string_builder + item_a.name + "\t" + item_a.imgPath + "\t" + item_a.price + "\t" + item_a.in_cart + "\t" + item_a.current_stock + "\v";
                }

                string_builder = string_builder.trim() + "\n";
            }

            if(string_builder.length > 0) {
                window.localStorage.setItem(sectionName, string_builder.trim());
            }
        }
        catch(ignored){
            console.log(ignored);
        }
    };
}

function parseSectionString(sectionString) {
    let page_sections = sectionString.split("\n");
    let localStorageObj = [];

    for(pagesec_a of page_sections) {
        let obj_builder = {};
        let pageSec = pagesec_a.split("~");

        obj_builder.sectionName = pageSec[0];
        obj_builder.sectionIdentifier = pageSec[1];
        let inventory_a = pageSec[2].split("\v");

        let inv_a = [];
        for(inv_item2 of inventory_a) {
            inv_item = inv_item2.split("\t");
            inv_a.push({
                name: inv_item[0],
                imgPath: inv_item[1],
                price: parseFloat(inv_item[2]),
                in_cart: parseInt(inv_item[3]),
                current_stock: parseInt(inv_item[4])
            })
        }
        obj_builder.inventory = inv_a;

        localStorageObj.push(obj_builder);
    }

    return localStorageObj;
}

function loadFromSession(pageSections, sectionName) {

    let localStorageString = window.localStorage.getItem(sectionName);
    let localStorageObj = [];

    try {
        localStorageObj = parseSectionString(localStorageString);
    }
    catch(ignored) {
        localStorageObj = pageSections;
        console.log(ignored);
    }

    // try {
    //     localStorageObj = JSON.parse(localStorageObj);
    // }
    // catch {
    //     localStorageObj = JSON.parse(JSON.stringify(pageSections));
    // }

    // if(!localStorageObj) {
    //     localStorageObj = JSON.parse(JSON.stringify(pageSections));
    // }

    try {
        for(let x=0; x<localStorageObj.length; x++) {
            for(let y=0; y<localStorageObj[x].inventory.length; y++) {
                pageSections[x].inventory[y].in_cart = localStorageObj[x].inventory[y].in_cart;
            }
        }
    }
    catch(ignored) {
        console.log(ignored);
    }
    
}

function sanityCheck() {
    const sanity_string = window.localStorage.getItem("sanity_check");

    if(sanity_string !== "0xfeedface") {
        window.localStorage.clear();
        window.localStorage.setItem("sanity_check", "0xfeedface");
    }

}

sanityCheck();
