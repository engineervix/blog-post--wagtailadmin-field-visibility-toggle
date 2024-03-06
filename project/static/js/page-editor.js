/**
 * Toggles visibility of a `contact_email` field's parent panel based on
 * its counterpart `use_designer_email` checkbox's state'.
 *
 * This is used on the page editor for ToyPages
 */
class ContactEmailVisibilityManager {
  constructor() {
    this.checkbox = document.querySelector(
      `input[type="checkbox"][name$="use_designer_email"][id$="id_use_designer_email"]`
    );
    this.emailField = document.querySelector(
      `input[type="email"][name$="contact_email"][id$="contact_email"]`
    );
  }

  toggleEmailField(checkbox) {
    const panelWrapper = this.emailField.closest(".w-panel__wrapper");
    panelWrapper.style.display = checkbox.checked ? "none" : "block";
  }

  initializeField(checkbox) {
    checkbox.addEventListener("change", () => this.toggleEmailField(checkbox));
  }

  initializePage() {
    this.initializeField(this.checkbox);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const cevm = new ContactEmailVisibilityManager();
  cevm.initializePage();
});

/**
 * Toggles visibility of a `end_date` field's parent panel based on
 * its counterpart `end_date_is_known` checkbox's state'.
 *
 * This is used on the page editor for ToyPages, specifically
 * on the **campaigns** InlinePanel.
 */
class EndDateVisibilityManager {
  constructor() {
    this.namePrefix = '[name^="campaigns-"]';
    this.idPrefix = '[id^="id_campaigns-"]';
    this.checkboxes = document.querySelectorAll(
      `input[type="checkbox"]${this.namePrefix}${this.idPrefix}[id$="-end_date_is_known"]`
    );
    this.addButton = document.querySelector("#id_campaigns-ADD");
  }

  toggleEndDateField(checkbox) {
    const match = checkbox.id.match(/-(\d+)-end_date_is_known/);
    const identifier = match ? match[1] : null;

    if (identifier !== null) {
      const endDateField = document.getElementById(
        `id_campaigns-${identifier}-end_date`
      );
      const panelWrapper = endDateField.closest(".w-panel__wrapper");
      panelWrapper.style.display = checkbox.checked ? "block" : "none";
    }
  }

  initializeFields(checkboxes) {
    checkboxes.forEach((checkbox) => {
      checkbox.addEventListener("change", () =>
        this.toggleEndDateField(checkbox)
      );
      this.toggleEndDateField(checkbox);
    });
  }

  initializePage() {
    this.initializeFields(this.checkboxes);

    this.addButton.addEventListener("click", () => {
      const newCheckboxes = this.addButton
        .closest(".w-panel__content")
        .querySelectorAll(
          `input[type="checkbox"]${this.namePrefix}${this.idPrefix}[id$="-end_date_is_known"]`
        );
      this.initializeFields(newCheckboxes);
    });
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const edvm = new EndDateVisibilityManager();
  edvm.initializePage();
});
