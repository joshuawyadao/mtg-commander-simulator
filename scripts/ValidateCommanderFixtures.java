import forge.GuiDesktop;
import forge.deck.CardPool;
import forge.deck.Deck;
import forge.deck.DeckFormat;
import forge.deck.DeckSection;
import forge.deck.io.DeckSerializer;
import forge.game.GameFormat;
import forge.gui.GuiBase;
import forge.item.PaperCard;
import forge.model.FModel;

import java.io.File;
import java.util.HashSet;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

/** Validates the four Stage A fixtures against the installed Forge release. */
public class ValidateCommanderFixtures {
    public static void main(String[] paths) {
        if (paths.length != 4) {
            throw new IllegalArgumentException("Expected four Commander deck paths");
        }

        GuiBase.setInterface(new GuiDesktop());
        FModel.initialize(null, null);
        GameFormat commanderFormat = FModel.getFormats().get("Commander");
        if (commanderFormat == null) {
            throw new IllegalStateException("Forge's Commander format data is unavailable");
        }

        Set<String> names = new HashSet<>();
        for (String path : paths) {
            File file = new File(path);
            if (!file.isFile()) {
                throw new IllegalArgumentException("Deck file is missing: " + path);
            }

            Deck deck = DeckSerializer.fromFile(file);
            if (deck == null) {
                throw new IllegalArgumentException("Forge could not parse deck: " + path);
            }

            String name = safeField(deck.getName(), "deck name", path);
            if (!names.add(name.toLowerCase(Locale.ROOT))) {
                throw new IllegalArgumentException("Duplicate deck name: " + name);
            }
            if (deck.getDeckFormat() != DeckFormat.Commander) {
                throw new IllegalArgumentException("Deck Type must be Commander: " + name);
            }
            if (deck.get(DeckSection.Commander) == null || deck.get(DeckSection.Commander).countAll() != 1) {
                throw new IllegalArgumentException("Expected exactly one commander: " + name);
            }
            if (deck.getMain().countAll() != 99) {
                throw new IllegalArgumentException("Expected exactly 99 main-deck cards: " + name);
            }
            for (Map.Entry<DeckSection, CardPool> section : deck) {
                if (section.getKey() != DeckSection.Main && section.getKey() != DeckSection.Commander
                        && !section.getValue().isEmpty()) {
                    throw new IllegalArgumentException("Unexpected " + section.getKey() + " section: " + name);
                }
            }
            for (Map.Entry<PaperCard, Integer> card : deck.getAllCardsInASinglePool()) {
                if (card.getKey().getRules().isUnsupported()) {
                    throw new IllegalArgumentException("Unsupported card in " + name + ": " + card.getKey().getName());
                }
            }

            String problem = DeckFormat.Commander.getDeckConformanceProblem(deck);
            if (problem == null) {
                problem = commanderFormat.getDeckConformanceProblem(deck);
            }
            if (problem != null) {
                throw new IllegalArgumentException("Illegal Commander deck " + name + ": " + problem);
            }

            String commander = safeField(deck.getCommanders().get(0).getName(), "commander name", path);
            String basename = safeField(file.getName(), "deck filename", path);
            System.out.println("STAGE_A_DECK\t" + basename + "\t" + name + "\t" + commander);
        }
    }

    private static String safeField(String value, String label, String path) {
        if (value == null || value.isBlank() || value.indexOf('\t') >= 0
                || value.indexOf('\r') >= 0 || value.indexOf('\n') >= 0) {
            throw new IllegalArgumentException("Invalid " + label + " in " + path);
        }
        return value;
    }
}
