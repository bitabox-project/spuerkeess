const preventMultipleSubmit = () => {

	let isSubmitting = false;

	const handleFormSubmit = () => {
		this.forms = document.querySelectorAll('.frame-type-form_formframework form');
		this.forms.forEach((form, keyForm) => {
			form.addEventListener('submit', (e) => {
				if (isSubmitting) {
					e.stopPropagation();
					e.preventDefault();
				}
				isSubmitting = true;
			})
		})
	}

	// Does it only after when page is ready
	document.addEventListener("DOMContentLoaded", handleFormSubmit);
}

preventMultipleSubmit();