document.getElementById("customFile").onchange = function () {
    document.getElementById("customFileLabel").innerText = this.value.replace(/.*[\/\\]/, '');
};
