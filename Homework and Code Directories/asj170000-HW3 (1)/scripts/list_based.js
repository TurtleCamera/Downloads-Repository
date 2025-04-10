// Load up all sections in the sidebar: 
function loadListSectionsInSidebar(sections, spContentsId) {
    // <label for="vegetables" style="word-wrap:break-word" onclick="toggle()">
    // <input id="vegetables" type="checkbox" value="vegetables">Vegetables
    // </label><br>

    const a = document.createElement("a");
    a.href = "#"

    text = document.createTextNode("Top of the page");
    a.appendChild(text);
    document.getElementById("spContents").appendChild(a);
    document.getElementById("spContents").appendChild(document.createElement("br"));

    for(section of sections) {
        const a = document.createElement("a");
        a.href = "#" + section.sectionIdentifier + "_table";

        text = document.createTextNode(section.sectionName);
        a.appendChild(text);
        document.getElementById("spContents").appendChild(a);
        document.getElementById("spContents").appendChild(document.createElement("br"));
    }
    
}