const input = document.querySelector("#chat-input");

const form = document.querySelector("#chat-form");

const suggestions = document.querySelectorAll(".suggestion-btn");

suggestions.forEach((button)=>{
    button.addEventListener("click", ()=>{
        input.value = button.textContent.trim();
        form.submit();
    });
});

form.addEventListener("submit", (event) => {
    event.preventDefault();
    const pesan = input.value.trim();
    if (pesan === "") {
    return;
    }
    fetch("/api/chat", {
        method: "POST",
        body: new URLSearchParams({
          pesan: pesan
        })
    })
    .then((response) => response.json())
    .then((data) => {
    buatBubble("Rio", pesan);
    buatBubble("AI", data.reply);
    input.value = "";
    });
    console.log(pesan);
    });

function buatBubble(sender, text){
  const bubble = document.createElement("div");
  bubble.className = "message " + sender;
  bubble.textContent = text;
  const chatHistory = document.querySelector(".chat-history");
  chatHistory.appendChild(bubble);
}