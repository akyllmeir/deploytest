document.addEventListener('DOMContentLoaded', () => {
  const doctorField = document.getElementById('id_doctor');
  const dateField = document.getElementById('id_date');
  const slotField = document.getElementById('id_slot');
  const slotGrid = document.getElementById('slotGrid');
  if (!doctorField || !dateField || !slotField || !slotGrid) return;

  const placeholderSelect = slotGrid.dataset.placeholderSelect || 'Выберите врача и дату';
  const placeholderEmpty = slotGrid.dataset.placeholderEmpty || 'Свободных слотов нет';
  const availableText = slotGrid.dataset.labelFree || 'СВОБОДНО';
  const bookedText = slotGrid.dataset.labelBusy || 'ЗАНЯТО';

  function clearGrid(text) {
    slotField.value = '';
    slotGrid.innerHTML = `<div class="subtle small">${text}</div>`;
  }

  function selectSlot(button) {
    slotGrid.querySelectorAll('.slot-card').forEach(el => el.classList.remove('selected'));
    button.classList.add('selected');
    slotField.value = button.dataset.value;
  }

  async function refreshSlots() {
    const doctorId = doctorField.value;
    const date = dateField.value;
    if (!doctorId || !date) {
      clearGrid(placeholderSelect);
      return;
    }
    try {
      const res = await fetch(`/api/doctor-slots/?doctor_id=${doctorId}&date=${date}`);
      const data = await res.json();
      slotGrid.innerHTML = '';
      if (!data.slots || !data.slots.length) {
        clearGrid(placeholderEmpty);
        return;
      }
      data.slots.forEach(slot => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = `slot-card ${slot.available ? 'available' : 'booked'}`;
        button.dataset.value = slot.value;
        button.innerHTML = `<div>${slot.label}</div><div class="small mt-1">${slot.available ? availableText : bookedText}</div>`;
        if (slot.available) {
          button.addEventListener('click', () => selectSlot(button));
        } else {
          button.disabled = true;
        }
        slotGrid.appendChild(button);
      });
    } catch (e) {
      clearGrid(placeholderEmpty);
    }
  }

  doctorField.addEventListener('change', refreshSlots);
  dateField.addEventListener('change', refreshSlots);
  if (doctorField.value && dateField.value) refreshSlots();
});
