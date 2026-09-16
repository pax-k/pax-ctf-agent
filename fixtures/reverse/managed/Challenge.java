public final class Challenge {
    public static void main(String[] args) {
        String value = args.length == 1 ? args[0] : "";
        System.out.println(new StringBuilder(value).reverse().toString());
    }
}
