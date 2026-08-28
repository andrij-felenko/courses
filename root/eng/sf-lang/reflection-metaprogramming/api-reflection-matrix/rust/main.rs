use proc_macro::TokenStream;
use syn::{parse_macro_input, DeriveInput, Data, Fields};
use quote::quote;

#[proc_macro_derive(MySerializer)]
pub fn derive_serializer(input: TokenStream) -> TokenStream {
    // 1. Парсинг вхідного потоку токенів у типізоване AST дерево
    let ast = parse_macro_input!(input as DeriveInput);
    let name = &ast.ident;

    // 2. Інтроспекція полів структури
    let field_names = match &ast.data {
        Data::Struct(data_struct) => match &data_struct.fields {
            Fields::Named(fields_named) => {
                fields_named.named.iter().map(|f| &f.ident).collect::<Vec<_>>()
            }
            _ => panic!("Підтримуються лише іменовані структури!"),
        },
        _ => panic!("Підтримуються лише структури, а не enum чи union!"),
    };

    // 3. Генерація коду за допомогою квазіцитування quote!
    let expanded = quote! {
        impl #name {
            pub fn print_fields(&self) {
                #(
                    println!("{}: {:?}", stringify!(#field_names), self.#field_names);
                )*
            }
        }
    };

    // 4. Повернення згенерованого AST назад у компілятор
    TokenStream::from(expanded)
}
