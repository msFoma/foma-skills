<img src="../assets/docs-quickstart.jpg" alt="Quick start" width="100%">

# 🚀 Быстрый старт

[← На главную](../../README.ru.md) · **Быстрый старт** · [Справочник по скиллам](skills.md) · [Как это работает](how-it-works.md) · [FAQ](faq.md)

Пять минут от установки до первой задачи. Ничего настраивать не нужно.

## Что понадобится

- **Claude Code** (терминал, приложение или расширение для IDE).
- Проект с git. Это желательно, не обязательно: так работают коммиты и обратимая уборка.
- На Windows нужен Git Bash: хуки пака написаны как shell-скрипты.

## 1. Установка

В Claude Code выполните:

```
/plugin marketplace add msFoma/foma-skills
/plugin install foma-skills@foma
```

То же из обычного терминала:

```bash
claude plugin marketplace add msFoma/foma-skills
claude plugin install foma-skills@foma
```

### Где включить: на всех проектах, на одном или для всей команды

| Область | Команда | Когда выбирать |
|---|---|---|
| `user` (по умолчанию) | `claude plugin install foma-skills@foma` | Хотите пак во всех своих проектах |
| `local` | `claude plugin install foma-skills@foma --scope local` | Только этот проект и только у вас; ничего не попадает в git. **Хороший выбор для пробы.** |
| `project` | `claude plugin install foma-skills@foma --scope project` | Вся команда: настройка записывается в `.claude/settings.json` проекта |

Для `local` и `project` запускайте команду из папки проекта.

## 2. Перезапустите Claude Code

Плагин и его хуки подключаются при старте сессии. Откройте новую сессию в папке проекта.

## 3. Убедитесь, что всё встало

```bash
claude plugin list                 # foma-skills@foma ... enabled
claude plugin details foma-skills  # состав и оценка токенов
```

В самой сессии наберите `/foma-skills:`: должен появиться список из 17 скиллов.

## 4. Скажите что-нибудь

Скиллы не нужно вызывать по имени. Опишите работу своими словами, подходящий скилл включится сам. С чего начать:

| Ситуация | Скажите | Что произойдёт |
|---|---|---|
| Пустой или новый проект | «Настрой этот проект для работы с Claude» | `groundwork` проверит проект, **покажет**, что хочет создать (`CLAUDE.md`, структура docs), и запишет после вашего «ок» |
| Есть идея | «Хочу сделать X» | `shaping` задаст вопросы и подготовит спеку |
| Есть спека, нужен порядок работ | «Составь план» | `planning` разложит работу на проверяемые задачи |
| Баг | «Почему падает Y?» | `debugging` найдёт причину, потом починит с тестом |
| Работа закончена | «Закоммить» | `committing` сделает маленькие коммиты и не станет пушить |
| Заканчиваете день | «Завершаем, продолжу завтра» | `handoff` оставит заметку для следующей сессии |

> [!TIP]
> Видите, что скилл сработал, по строке вызова инструмента `Skill` в сессии. Если нужный скилл молчит, вызовите его вручную: `/foma-skills:planning`, `/foma-skills:tidying` и так далее.

## Куда пак кладёт файлы

Пак пишет только в понятные места и **после вашего «ок»**:

| Путь | Что там | Кто пишет |
|---|---|---|
| `CLAUDE.md` (блок «Commands · Where things live · Workflow») | Короткий договор проекта: команды, где что лежит | `groundwork` |
| `docs/specs/<имя>.md` | Утверждённая спека фичи | `shaping` |
| `docs/plans/<фича>/plan.md`, `docs/plans/archive/` | План и завершённые планы | `planning`, `executing` |
| `docs/design/`, `DESIGN.md` | Варианты дизайна и ваш выбор | `design-interview` |
| `docs/decisions.md` | Записи о важных решениях | `documenting` |
| `.claude/agents/` | Помощники `implementer`, `reviewer`, `explorer` | `groundwork` |
| `.scratch/handoff.md` | Заметка на следующую сессию (до 20 строк) | `handoff` |
| `.scratch/fires.jsonl` | Журнал срабатываний скиллов, только локально | хук пака |
| `.trash/` | Удалённое обратимо, с описью `MANIFEST` | `tidying` |

> [!NOTE]
> Папку `.scratch/` стоит добавить в `.gitignore` проекта (или в `.git/info/exclude`): это рабочие файлы, коммитить их не нужно.

## Обновление

```bash
claude plugin marketplace update foma
claude plugin update foma-skills@foma
```

Затем перезапустите сессию.

## Отключение и удаление

```bash
claude plugin disable foma-skills@foma     # выключить, не удаляя
claude plugin enable foma-skills@foma      # включить обратно
claude plugin uninstall foma-skills@foma   # удалить
```

Файлы, которые скиллы создали в вашем проекте (`docs/`, `CLAUDE.md`), остаются: они ваши.

## Что дальше

- Прочитайте [справочник по скиллам](skills.md): что каждый делает, что меняет и чего не делает.
- Если что-то не срабатывает или непонятно, загляните в [FAQ](faq.md).
- Через 2–3 недели работы выполните `/foma-skills:tuning`: он покажет, какие скиллы вам ни разу не пригодились.
