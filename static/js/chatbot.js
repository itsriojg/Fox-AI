const input = document.querySelector("#chat-input");

const form = document.querySelector("#chat-form");

const suggestions = document.querySelectorAll(".suggestion-btn");

suggestions.forEach((button)=>{
    button.addEventListener("click", ()=>{
        input.value = button.textContent.trim();
        form.submit();
    });
});