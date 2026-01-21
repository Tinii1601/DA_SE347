(function () {
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === name + "=") {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function toggleIcon(btn, inWishlist) {
        const icon = btn.querySelector("i");
        if (!icon) return;
        if (inWishlist) {
            icon.classList.remove("bi-heart");
            icon.classList.add("bi-heart-fill");
        } else {
            icon.classList.remove("bi-heart-fill");
            icon.classList.add("bi-heart");
        }
    }

    document.addEventListener("DOMContentLoaded", function () {
        const buttons = document.querySelectorAll(".wishlist-toggle-btn[data-product-id]");
        if (!buttons.length) return;

        const csrftoken = getCookie("csrftoken");

        buttons.forEach((btn) => {
            btn.addEventListener("click", function (e) {
                e.preventDefault();
                const productId = btn.getAttribute("data-product-id");
                if (!productId) return;

                fetch(`/users/wishlist/toggle/${productId}/`, {
                    method: "POST",
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": csrftoken || "",
                    },
                })
                    .then((res) => {
                        if (res.redirected && res.url.includes("/users/login/")) {
                            window.location.href = res.url;
                            return null;
                        }
                        return res.json();
                    })
                    .then((data) => {
                        if (!data) return;
                        const added = !!data.added;
                        btn.setAttribute("data-in-wishlist", added ? "1" : "0");
                        toggleIcon(btn, added);
                    })
                    .catch(() => { });
            });
        });
    });
})();
