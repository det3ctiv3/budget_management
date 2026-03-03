export function formDataAsJson(form) {
  const data = Object.fromEntries(new FormData(form).entries());
  for (const [key, value] of Object.entries(data)) {
    if (value === "") {
      delete data[key];
    }
  }
  return data;
}
