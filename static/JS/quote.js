document.getElementById("quote-form").addEventListener("submit", function(event) {
    event.preventDefault();
    
    var symbol = document.getElementById("symbol-input").value;
    
    fetch("/quote/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
            symbol: symbol
        })
    })
    .then(response => response.text())
    .then(data => {
        var priceMessage = document.getElementById("price-message");
        
        priceMessage.classList.remove("success", "error");
        
        if (data.includes("costs")) {
            priceMessage.innerHTML = data;
            priceMessage.classList.add("success");
        } else {
            priceMessage.innerHTML = "Stock symbol not found.";
            priceMessage.classList.add("error");
        }
    })
    .catch(error => {
        console.error("Error:", error);
        var priceMessage = document.getElementById("price-message");
        priceMessage.innerHTML = "An error occurred while fetching the price.";
        priceMessage.classList.add("error");
    });
});
