(() => {
    const chatbotToggler = document.querySelector("#chatbot-toggler");
    const chatbotWindow = document.querySelector("#chatbot-window");
    const chatInput = document.querySelector("#chatbot-input textarea");
    const sendChatBtn = document.querySelector("#chatbot-input button");
    const chatbox = document.querySelector("#chatbot-messages");

    if (!chatbotWindow || !chatInput || !sendChatBtn || !chatbox || !chatbotToggler) {
        return;
    }

    const askUrl = chatbotWindow.getAttribute("data-ask-url") || "";
    const csrfToken = chatbotWindow.getAttribute("data-csrf") || "";

    let userMessage = null;
    const inputInitHeight = chatInput.scrollHeight;

    const createChatLi = (message, className) => {
        const chatLi = document.createElement("li");
        chatLi.classList.add("chat-message", className);
        const content = className === "outgoing"
            ? `<div class="message-content"></div>`
            : `<span class="bi bi-robot"></span><div class="message-content"></div>`;
        chatLi.innerHTML = content;

        if (className === "outgoing") {
            chatLi.querySelector(".message-content").textContent = message;
        } else {
            chatLi.querySelector(".message-content").innerHTML = message;
        }
        return chatLi;
    };

    const updateWindowSizeForProducts = (count) => {
        if (count >= 5) {
            chatbotWindow.classList.add("wide");
        } else {
            chatbotWindow.classList.remove("wide");
        }
    };

    const generateResponse = (chatElement) => {
        const messageElement = chatElement.querySelector(".message-content");

        fetch(askUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({ message: userMessage })
        }).then(res => res.json()).then(data => {
            if (data.error) {
                messageElement.textContent = "Lỗi: " + data.error;
            } else if (data.response) {
                let formattedText = data.response
                    .replace(/\n/g, '<br>')
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

                if (data.products && data.products.length > 0) {
                    chatElement.classList.add("has-products");
                    updateWindowSizeForProducts(data.products.length);
                    formattedText += '<div class="chat-products">';
                    data.products.forEach(p => {
                        formattedText += `
                            <a href="${p.url}" class="chat-product-card" target="_blank">
                                <img src="${p.image}" alt="${p.name}" onerror="this.src='/static/img/default-book-cover.jpg'">
                                <div class="info">
                                    <h4>${p.name}</h4>
                                    <span>${p.price}</span>
                                </div>
                            </a>
                        `;
                    });
                    formattedText += '</div>';
                } else {
                    chatElement.classList.remove("has-products");
                    updateWindowSizeForProducts(0);
                }

                messageElement.innerHTML = formattedText;
            } else {
                messageElement.textContent = "Không có phản hồi.";
            }
        }).catch((err) => {
            console.error(err);
            messageElement.textContent = "Xin lỗi, đã có lỗi mạng xảy ra.";
            chatElement.classList.remove("has-products");
            updateWindowSizeForProducts(0);
        }).finally(() => {
            chatbox.scrollTo(0, chatbox.scrollHeight);
        });
    };

    const handleChat = () => {
        userMessage = chatInput.value.trim();
        if (!userMessage) return;

        chatInput.value = "";
        chatInput.style.height = `${inputInitHeight}px`;

        chatbox.appendChild(createChatLi(userMessage, "outgoing"));
        chatbox.scrollTo(0, chatbox.scrollHeight);

        const incomingChatLi = createChatLi("Đang suy nghĩ...", "incoming");
        chatbox.appendChild(incomingChatLi);
        chatbox.scrollTo(0, chatbox.scrollHeight);

        generateResponse(incomingChatLi);
    };

    chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
            e.preventDefault();
            handleChat();
        }
    });

    sendChatBtn.addEventListener("click", handleChat);

    chatbotToggler.addEventListener("click", () => {
        document.body.classList.toggle("show-chatbot");
    });
})();
