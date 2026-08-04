const messages = document.querySelector("#messages");
const welcomeScreen = document.querySelector(".welcome-screen");
const input = document.querySelector("#chat-input");
const form = document.querySelector("#chat-form");
const suggestions = document.querySelectorAll(".suggestion-btn");

suggestions.forEach((button)=>{
  button.addEventListener("click", ()=>{
    const pesan = button.textContent.trim();
      kirimPesan(pesan);
  });
});

function kirimPesan(pesan){
  fetch("/api/chat", {
      method: "POST",
      body: new URLSearchParams({
      pesan: pesan
    })
  })
    .then((response) => response.json())
    .then((data) => {
      welcomeScreen.style.display = "none";
      buatBubble("Rio", pesan);
      buatBubble("AI", data.reply);
      input.value = "";
    });
}

form.addEventListener("submit", (event) => {
    event.preventDefault();
    const pesan = input.value.trim();
    if (pesan === "") {
    return;
    }
    kirimPesan(pesan);
    console.log(pesan);
    });

function buatBubble(sender, text){
  const bubble = document.createElement("div");
  bubble.className = "message " + sender;
  bubble.textContent = text;
  messages.appendChild(bubble);
}

if(messages.children.length > 0){
  welcomeScreen.style.display = "none";
}