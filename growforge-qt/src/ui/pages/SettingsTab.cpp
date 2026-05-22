#include "ui/pages/SettingsTab.h"
#include "ui/MainWindow.h"
#include "ui/Toast.h"
#include "ui/widgets/CommonWidgets.h"
#include "app/Config.h"
#include "app/Theme.h"
#include "app/Paths.h"
#include "data/Database.h"
#include "core/Exporter.h"

#include <QFormLayout>
#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QComboBox>
#include <QSpinBox>
#include <QPushButton>
#include <QLabel>
#include <QCoreApplication>
#include <QMessageBox>
#include <QFile>
#include <QTextStream>

SettingsTab::SettingsTab(MainWindow *main) : ScrollPage(main) {}

void SettingsTab::refresh() {
    auto *root = resetContent();
    root->addWidget(makePageHeader("Settings", "Preferences, units, reminders, and data."));

    // ── Appearance ──
    auto *appCard = new Card("Appearance");
    auto *appForm = new QFormLayout;
    auto *theme = new QComboBox;
    theme->addItem("Dark (command center)", "dark");
    theme->addItem("Light", "light");
    theme->setCurrentIndex(Theme::currentThemeName() == "light" ? 1 : 0);
    connect(theme, &QComboBox::currentIndexChanged, this, [this, theme](int) {
        m_main->switchTheme(theme->currentData().toString());
    });
    appForm->addRow("Theme", theme);
    appCard->addLayout(appForm);
    root->addWidget(appCard);

    // ── Grow profile ──
    auto *profCard = new Card("Grow Profile");
    auto *profForm = new QFormLayout;
    auto *mode = new QComboBox;
    mode->addItem("Beginner", "beginner");
    mode->addItem("Advanced", "advanced");
    mode->setCurrentIndex(Db::getSettingStr("mode", "beginner") == "advanced" ? 1 : 0);
    connect(mode, &QComboBox::currentIndexChanged, this, [mode](int) {
        Db::setSetting("mode", mode->currentData().toString());
    });
    profForm->addRow("Experience mode", mode);
    profCard->addLayout(profForm);
    root->addWidget(profCard);

    // ── Units ──
    auto *unitCard = new Card("Units");
    auto *unitForm = new QFormLayout;
    auto *temp = new QComboBox;
    temp->addItem("Celsius (°C)", "C");
    temp->addItem("Fahrenheit (°F)", "F");
    temp->setCurrentIndex(Db::getSettingStr("temp_unit", "C") == "F" ? 1 : 0);
    connect(temp, &QComboBox::currentIndexChanged, this, [this, temp](int) {
        Db::setSetting("temp_unit", temp->currentData().toString());
        Toast::show(this, "Temperature unit saved.", Toast::Success);
    });
    unitForm->addRow("Temperature", temp);
    unitCard->addLayout(unitForm);
    root->addWidget(unitCard);

    // ── Reminders ──
    auto *remCard = new Card("Reminders");
    auto *remForm = new QFormLayout;
    auto *interval = new QSpinBox; interval->setRange(5, 3600); interval->setSuffix(" s");
    interval->setValue(Db::getSettingInt("reminder_check_interval", 60));
    auto *water = new QSpinBox; water->setRange(1, 30); water->setSuffix(" days");
    water->setValue(Db::getSettingInt("default_water_interval_days", 2));
    auto *feed = new QSpinBox; feed->setRange(1, 30); feed->setSuffix(" days");
    feed->setValue(Db::getSettingInt("default_feed_interval_days", 4));
    auto *save = new QPushButton("Save reminder settings");
    save->setProperty("variant", "primary");
    connect(save, &QPushButton::clicked, this, [this, interval, water, feed]() {
        Db::setSetting("reminder_check_interval", QString::number(interval->value()));
        Db::setSetting("default_water_interval_days", QString::number(water->value()));
        Db::setSetting("default_feed_interval_days", QString::number(feed->value()));
        Toast::show(this, "Reminder settings saved.", Toast::Success);
    });
    remForm->addRow("Check interval", interval);
    remForm->addRow("Default watering", water);
    remForm->addRow("Default feeding", feed);
    remCard->addLayout(remForm);
    remCard->addWidget(save);
    root->addWidget(remCard);

    // ── Data ──
    auto *dataCard = new Card("Data");
    dataCard->addWidget(makeKeyValue("Database", Paths::dbPath()));
    dataCard->addWidget(makeKeyValue("Plants", QString::number(Db::count("plants"))));
    dataCard->addWidget(makeKeyValue("Events", QString::number(Db::count("events"))));
    dataCard->addWidget(makeKeyValue("Strains", QString::number(Db::count("strains"))));
    auto *exportBtn = new QPushButton("Export all events to CSV");
    connect(exportBtn, &QPushButton::clicked, this, [this]() {
        const QString path = Paths::exportsDir() + "/all_events.csv";
        if (Exporter::exportEventsCsv(Db::getAll("events", QString(), {}, "event_date DESC"), path))
            Toast::show(this, "Events exported to the exports folder.", Toast::Success, 5000);
        else
            Toast::show(this, "Export failed.", Toast::Error);
    });
    dataCard->addWidget(exportBtn);

    // Opt-in demo data — new installs start empty.
    auto *sampleBtn = new QPushButton("Load sample data");
    sampleBtn->setToolTip("Add a few demo plants, environments, and journal entries to explore the app.");
    connect(sampleBtn, &QPushButton::clicked, this, [this]() {
        if (Db::count("plants") > 0) {
            QMessageBox box(this);
            box.setWindowTitle("Load Sample Data");
            box.setText("Add demo plants, environments, and journal entries?");
            box.setInformativeText("You already have data — sample entries will be added alongside it.");
            box.setStandardButtons(QMessageBox::Yes | QMessageBox::No);
            box.setDefaultButton(QMessageBox::No);
            if (box.exec() != QMessageBox::Yes) return;
        }
        QFile f(":/sample_data.sql");
        if (f.open(QIODevice::ReadOnly | QIODevice::Text)) {
            Db::runScript(QTextStream(&f).readAll());
            Toast::show(this, "Sample data loaded.", Toast::Success);
            m_main->refreshChrome();
            refresh();
        } else {
            Toast::show(this, "Sample data unavailable.", Toast::Error);
        }
    });
    dataCard->addWidget(sampleBtn);
    root->addWidget(dataCard);

    // ── About ──
    auto *about = new Card("About");
    about->addWidget(makeKeyValue("Version", Config::APP_VERSION));
    about->addWidget(makeKeyValue("Tagline", Config::APP_TAGLINE));
    auto *local = makeMuted("100% local & offline. Your grow data never leaves this machine.");
    about->addWidget(local);
    root->addWidget(about);

    root->addStretch();
}
